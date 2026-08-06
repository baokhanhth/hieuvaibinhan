from django.db.models import Q,  Sum, Count, F
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncDay

from .models import SalesOrder,  SalesOrderItem, Product
from django.http import JsonResponse

def success_response(data=None, message="Thành công.", status=200):
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status,
    )

def error_response(message="Có lỗi xảy ra.", status=400):
    return JsonResponse(
        {
            "success": False,
            "message": message,
            "data": None,
        },
        status=status,
    )
    
def process_search_order_list(keyword="", status=""):
    orders = (SalesOrder.objects.select_related("employee").order_by("-created_at"))

    keyword = keyword.strip()

    if keyword:
        filters = (
            Q(employee__username__icontains=keyword) |
            Q(employee__full_name__icontains=keyword)
        )

        code = keyword.upper().replace(" ", "").replace("HDB", "").lstrip("0")

        if code.isdigit():
            filters |= Q(pk=int(code))

        orders = orders.filter(filters)

    if status:
        orders = orders.filter(status=status)

    return orders

def process_reports_data(filter_type="30days", from_date_str=None, to_date_str=None):
    now = timezone.now()
    start_date = None
    end_date = now

    if filter_type == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "7days":
        start_date = now - timedelta(days=7)
    elif filter_type == "30days":
        start_date = now - timedelta(days=30)
    elif filter_type == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "custom" and from_date_str and to_date_str:
        try:
            parsed_start = datetime.strptime(from_date_str, "%Y-%m-%d")
            parsed_end = datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            
            parsed_start = timezone.make_aware(parsed_start)
            parsed_end = timezone.make_aware(parsed_end)
            
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) if parsed_start > now else parsed_start
            end_date = now if parsed_end > now else parsed_end

            if start_date > end_date:
                start_date, end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0), start_date.replace(hour=23, minute=59, second=59)

            if end_date > now:
                end_date = now

        except ValueError:
            start_date = now - timedelta(days=30)

    if not start_date:
        start_date = now - timedelta(days=30)

    orders = SalesOrder.objects.filter(
        status=SalesOrder.Status.COMPLETED,
        created_at__gte=start_date,
        created_at__lte=end_date
    )

    total_revenue = orders.aggregate(sum=Sum('final_amount'))['sum'] or 0
    total_orders = orders.count()

    order_items = SalesOrderItem.objects.filter(order__in=orders)

    if total_orders == 0:
        best_sellers = []
        slow_sellers = []
    else:
        best_sellers = list(
            order_items
            .values(product_name=F('product__name'))
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5]
        )

        active_products = Product.objects.filter(status=Product.Status.ACTIVE)
        sales_dict = {
            item['product__id']: item['total'] 
            for item in order_items.values('product__id').annotate(total=Sum('quantity'))
        }
        
        slow_sellers_list = [
            {"product_name": prod.name, "total_qty": float(sales_dict.get(prod.id, 0))}
            for prod in active_products
        ]
        slow_sellers_list.sort(key=lambda x: x['total_qty'])
        slow_sellers = slow_sellers_list[:5]

    # 5. Thống kê doanh thu theo ngày
    revenue_by_date = (
        orders
        .annotate(date=TruncDay('created_at'))
        .values('date')
        .annotate(
            sum_revenue=Sum('final_amount'),
            order_count=Count('id')
        )
        .order_by('date')
    )
    
    revenue_map = {
        item['date'].strftime('%Y-%m-%d'): {
            'revenue': float(item['sum_revenue'] or 0),
            'orders': int(item['order_count'] or 0)
        } 
        for item in revenue_by_date if item['date']
    }

    chart_labels = []
    chart_revenue_data = []
    chart_orders_data = []

    current_day = start_date.date()
    final_day = end_date.date()

    while current_day <= final_day:
        day_str = current_day.strftime('%Y-%m-%d')
        chart_labels.append(day_str)
        
        if day_str in revenue_map:
            chart_revenue_data.append(revenue_map[day_str]['revenue'])
            chart_orders_data.append(revenue_map[day_str]['orders'])
        else:
            chart_revenue_data.append(0.0)
            chart_orders_data.append(0)
            
        current_day += timedelta(days=1)

    return {
        "success": True,
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "chart": {
            "labels": chart_labels,
            "revenue": chart_revenue_data,
            "orders": chart_orders_data
        },
        "best_sellers": best_sellers,
        "slow_sellers": slow_sellers
    }