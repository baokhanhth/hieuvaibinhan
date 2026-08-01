from datetime import datetime, timedelta
import json
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count
from inventory.models import Product
from accounts.models import User
from django.shortcuts import redirect
from django.urls import reverse
from .models import SalesOrder, SalesOrderItem
from django.db import transaction
from inventory.utils import process_search_products
from django.utils import timezone
from decimal import Decimal
from django.db.models.functions import TruncMonth, TruncDay

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
    
def get_orders():
    return (
                SalesOrder.objects.select_related("employee").order_by("-created_at")
    )

def get_order(order_id):
    return get_object_or_404(
        SalesOrder.objects
        .select_related("employee")
        .prefetch_related("items__product"),
        pk=order_id,
    )
    
def get_or_create_draft_order(employee):
    order = (   SalesOrder.objects .filter(employee=employee, status=SalesOrder.Status.DRAFT,)
                .order_by("-created_at").first())

    if order:
        return order

    return process_create_order(employee)

def product_search_sale(request):
    if request.method != "GET":
        return error_response("Method not allowed.", status=405)

    keyword = request.GET.get("q", "").strip()
    products = process_search_products(keyword)

    data = [{   "id": p.id,
                "name": p.name,
                "selling_price": float(p.selling_price),
    } for p in products]

    return success_response(data=data)

@transaction.atomic
def process_create_order(employee, discount=0):
    return SalesOrder.objects.create(
        employee=employee,
        discount=discount,
        status=SalesOrder.Status.DRAFT,
    )

def can_edit_order(user, order):
    if user.is_owner:
        return order.status == SalesOrder.Status.DRAFT

    if user.is_employee:
        return order.status == SalesOrder.Status.DRAFT

    return False


def can_delete_order(user, order):
    if user.is_owner:
        return order.status in (
            SalesOrder.Status.DRAFT,
            SalesOrder.Status.COMPLETED,
        )

    if user.is_employee:
        return order.status == SalesOrder.Status.DRAFT

    return False


@transaction.atomic
def process_delete_order(order, user):

    # Nhân viên: Chỉ được xóa hóa đơn nháp.
    # Chủ cửa hàng: Được xóa mọi hóa đơn. Nếu hóa đơn đã thanh toán thì cập nhật thành hủy và hoàn tồn kho.
    
    if not can_delete_order(user, order):
        raise ValidationError("Bạn không có quyền xóa hóa đơn đã thanh toán.")

    if order.status == SalesOrder.Status.DRAFT:
        order.delete()
        return
        
    if order.status == SalesOrder.Status.COMPLETED:
        process_cancel(order)
        return
    
    raise ValidationError("Không thể xóa hóa đơn.")

@transaction.atomic
def process_add_order_item(order, product, quantity):
    if order.status != SalesOrder.Status.DRAFT:
        raise ValidationError("Không thể sửa hóa đơn đã thanh toán.")

    if quantity <= 0:
        raise ValidationError(
            "Số lượng phải lớn hơn 0."
        )

    item, created = SalesOrderItem.objects.get_or_create(   order=order,
                                                            product=product,
                                                            defaults={
                                                                "quantity": quantity,
                                                                "unit_price": product.selling_price,
                                                            },)

    if not created:
        item.quantity += quantity
        item.save()

    _update_order_total(order)

    return item

@transaction.atomic
def process_update_order_item(item, quantity):
    order = item.order

    if order.status != SalesOrder.Status.DRAFT:
        raise ValidationError("Không thể sửa hóa đơn đã thanh toán.")

    if quantity <= 0:
        raise ValidationError("Số lượng phải lớn hơn 0.")

    item.quantity = quantity

    item.save()

    _update_order_total(order)

    return item


@transaction.atomic
def process_delete_order_item(item):
    order = item.order
    if order.status != SalesOrder.Status.DRAFT:
        raise ValidationError( "Không thể sửa hóa đơn đã thanh toán.")
    item.delete()

    _update_order_total(order)

@transaction.atomic
def process_checkout(order):

    if order.status != SalesOrder.Status.DRAFT:
        raise ValidationError("Hóa đơn không hợp lệ.")

    items = order.items.select_related("product")

    if not items.exists():
        raise ValidationError("Hóa đơn chưa có sản phẩm.")

    for item in items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock_quantity < item.quantity:
            raise ValidationError(f"Sản phẩm '{product.name}' không đủ tồn kho.")

    for item in items:

        product = Product.objects.select_for_update().get(pk=item.product_id)
        product.stock_quantity -= item.quantity
        product.save(update_fields=["stock_quantity"])
    _update_order_total(order)

    order.status = SalesOrder.Status.COMPLETED

    order.completed_at = timezone.now()

    order.save(update_fields=[ "status","updated_at","completed_at",])

    return order

@transaction.atomic
def process_cancel(order):
    if order.status != SalesOrder.Status.COMPLETED:
        raise ValidationError("Chỉ có thể hủy hóa đơn ch thanh toán.")

    for item in order.items.select_related("product"):
        product = Product.objects.select_for_update().get(  pk=item.product_id)
        product.stock_quantity += item.quantity
        product.save( update_fields =   ["stock_quantity",])

    order.status = SalesOrder.Status.CANCELLED

    order.save  (update_fields=[    "status",
                                    "updated_at",])

    return order

def _update_order_total(order):
    total = (   order.items.aggregate(  total = Sum("subtotal"))["total"] or 0)
    order.total_amount = total
    order.final_amount = max(0, total - order.discount,)
    order.save(
        update_fields=[
            "total_amount",
            "final_amount",
            "updated_at",
        ]
    )
    
@login_required(login_url="login")
def homepage(request):
    order = get_or_create_draft_order(request.user)
        
    return render(request,"sales/homepage.html", {"order": order})

@login_required(login_url="login")
def reports(request):
    if not request.user.is_owner:
        return redirect("sales:homepage")
    return render(request, "sales/reports.html")

@login_required(login_url="login")
def reports_data(request):
    filter_type = request.GET.get("filter", "today")
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    now = timezone.now()
    start_date = None
    end_date = now

    # Xác định khoảng thời gian theo bộ lọc
    if filter_type == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "7days":
        start_date = now - timedelta(days=7)
    elif filter_type == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "custom" and from_date_str and to_date_str:
        try:
            parsed_start = datetime.strptime(from_date_str, "%Y-%m-%d")
            parsed_end = datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            
            # Đồng bộ hóa múi giờ để khớp hoàn toàn với biến 'now' (offset-aware)
            parsed_start = timezone.make_aware(parsed_start)
            parsed_end = timezone.make_aware(parsed_end)
            
            if parsed_start > now:
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = parsed_start

            if parsed_end > now:
                end_date = now
            else:
                end_date = parsed_end
        except ValueError:
            pass

    # Query hóa đơn đã thanh toán trong khoảng thời gian hợp lệ
    orders = SalesOrder.objects.filter(status=SalesOrder.Status.COMPLETED)
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)

    # 1. Tính KPIs tổng quan
    total_revenue = orders.aggregate(sum=Sum('final_amount'))['sum'] or 0
    total_orders = orders.count()

    # 2. Thống kê sản phẩm bán chạy / bán chậm
    order_items = SalesOrderItem.objects.filter(order__in=orders)

    if total_orders == 0:
        best_sellers = []
        slow_sellers = []
    else:
        # BÁN CHẠY: Lấy các mặt hàng bán nhiều nhất từ các hóa đơn (Sắp xếp giảm dần số lượng)
        best_sellers = list(
            order_items
            .values(product_name=F('product__name'))
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5]
        )

        # BÁN CHẬM: Lấy toàn bộ sản phẩm Active, đối chiếu với số lượng đã bán để tìm món bán ít nhất
        active_products = Product.objects.filter(status=Product.Status.ACTIVE)
        sales_dict = {
            item['product__id']: item['total'] 
            for item in order_items.values('product__id').annotate(total=Sum('quantity'))
        }
        
        slow_sellers_list = []
        for prod in active_products:
            sold_qty = float(sales_dict.get(prod.id, 0))
            slow_sellers_list.append({"product_name": prod.name, "total_qty": sold_qty})
        
        # Sắp xếp tăng dần (số lượng từ thấp lên cao) để lấy các món bán chậm nhất
        slow_sellers_list.sort(key=lambda x: x['total_qty'])
        slow_sellers = slow_sellers_list[:5]

    # 3. Thống kê doanh thu và số lượng đơn hàng theo ngày (Đảm bảo lấp đầy khoảng thời gian)
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
    
    # Chuyển kết quả database thành một dictionary để tra cứu nhanh theo ngày (YYYY-MM-DD)
    revenue_map = {
        item['date'].strftime('%Y-%m-%d'): {
            'revenue': float(item['sum_revenue'] or 0),
            'orders': int(item['order_count'] or 0)
        } 
        for item in revenue_by_date if item['date']
    }

    # Sinh danh sách đầy đủ tất cả các ngày từ start_date đến end_date
    chart_labels = []
    chart_revenue_data = []
    chart_orders_data = []

    # Ép kiểu start_date và end_date về dạng date thuần túy để chạy vòng lặp
    current_day = start_date.date() if start_date else end_date.date()
    final_day = end_date.date()

    while current_day <= final_day:
        day_str = current_day.strftime('%Y-%m-%d')
        chart_labels.append(day_str)
        
        # Nếu ngày đó có doanh thu thì lấy, không thì mặc định là 0
        if day_str in revenue_map:
            chart_revenue_data.append(revenue_map[day_str]['revenue'])
            chart_orders_data.append(revenue_map[day_str]['orders'])
        else:
            chart_revenue_data.append(0.0)
            chart_orders_data.append(0)
            
        current_day += timedelta(days=1)

    return JsonResponse({
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
    })

    
@login_required(login_url="login")
def orders(request):
    if request.method == "GET":
        query = request.GET.get("q", "").strip()
        selected_status = request.GET.get("status", "").strip()
        orders = get_orders()

        if query:
            filters = Q(employee__full_name__icontains=query)
            code_value = query.upper().removeprefix("HDB")
            if code_value.isdigit():
                filters |= Q(pk=int(code_value))
            orders = orders.filter(filters)

        valid_statuses = {value for value, _label in SalesOrder.Status.choices}
        if selected_status in valid_statuses:
            orders = orders.filter(status=selected_status)

        data = []
        for order in orders:
            data.append({
                "id": order.id,
                "employee": order.employee.full_name,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "discount": float(order.discount),
                "final_amount": float(order.final_amount),
                "created_at": order.created_at.strftime("%d/%m/%Y %H:%M"),
            })
        return success_response(data=data)

    return error_response("Method not allowed.", status=405,)

@login_required(login_url="login")
def new_draft(request):
    if request.method != "POST":
        return error_response("Method not allowed.",status=405,)
    try:
        draft = (SalesOrder.objects.filter(employee=request.user,status=SalesOrder.Status.DRAFT,).first())

        if draft:   draft.delete()

        new_order = process_create_order(request.user)

        return success_response(
            data={"order_id": new_order.id,},
            message="Đã tạo hóa đơn mới.",
        )

    except Exception:
        return error_response("Không thể tạo hóa đơn mới.", status=500,)
        
@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_order(order_id)
    return render(  request, "sales/order_detail.html",
        {
            "order": order,
            "items": order.items.select_related("product"),
            "can_delete": can_delete_order(request.user, order),
        },
    )

@login_required(login_url="login")
def order_data(request, order_id):
    order = get_order(order_id)

    data = {
        "id": order.id,
        "order_code": order.order_code,
        "status": order.status,
        "discount": float(order.discount),
        "total_amount": float(order.total_amount),
        "final_amount": float(order.final_amount),
        "items": []
    }

    for item in order.items.select_related("product"):
        data["items"].append({
            "id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": float(item.quantity),
            "unit_price": float(item.unit_price),
            "subtotal": float(item.subtotal),
        })

    return success_response(data=data)
    
@login_required(login_url="login")
def delete_order(request, order_id):

    if request.method != "DELETE":
        return error_response(
            "Method not allowed.",
            status=405,
        )

    order = get_order(order_id)

    try:

        is_draft = (
            order.status
            == SalesOrder.Status.DRAFT
        )

        process_delete_order(
            order,
            request.user,
        )

        return success_response(
            message=(
                "Đã xóa hóa đơn."
                if is_draft
                else "Đã hủy hóa đơn."
            )
        )

    except ValidationError as e:
        return error_response(e.messages[0])

    except Exception:
        return error_response("Không thể xóa hóa đơn.",status=500,)
        
          
@login_required(login_url="login")
def order_items(request, order_id):
    if request.method != "POST":
        return error_response("Method not allowed.",status=405,)

    try:
        body = json.loads(request.body)

        product_id = body.get("product_id")
        quantity = body.get("quantity")

        if product_id is None:
            return error_response("Thiếu product_id.")

        if quantity is None:
            return error_response("Thiếu quantity.")

        order = get_object_or_404(SalesOrder, pk=order_id,)

        if order.status != SalesOrder.Status.DRAFT:
            raise ValidationError("Chỉ có thể thêm sản phẩm vào hóa đơn nháp.")

        if not (request.user.is_owner or order.employee == request.user):
            raise ValidationError("Bạn không có quyền chỉnh sửa hóa đơn này.")

        product = get_object_or_404(Product, pk=product_id,)

        item = process_add_order_item(order, product, Decimal(str(quantity)),)

        return success_response(    data={"item_id": item.id,},
                                    message="Thêm sản phẩm thành công.",
                                    status=201,)

    except ValidationError as e:
        return error_response(e.messages[0])

    except json.JSONDecodeError:
        return error_response("Dữ liệu JSON không hợp lệ.")

    except Exception:
        return error_response("Không thể thêm sản phẩm.",status=500,)

@login_required(login_url="login")
def order_item_detail(request, order_id, item_id):
    item = get_object_or_404(SalesOrderItem, pk=item_id, order_id=order_id,)

    if request.method == "PUT":
        try:
            body = json.loads(request.body)
            quantity = body.get("quantity")
            if quantity is None:
                return error_response( "Thiếu quantity.")

            process_update_order_item(item, Decimal(str(quantity)),)

            return success_response(message="Cập nhật sản phẩm thành công.")

        except ValidationError as e:
            return error_response(e.messages[0])

        except json.JSONDecodeError:
            return error_response("Dữ liệu JSON không hợp lệ.")

        except Exception:
            return error_response("Không thể cập nhật sản phẩm.",status=500,
            )

    elif request.method == "DELETE":
        try:
            process_delete_order_item(item)
            return success_response(message="Đã xóa sản phẩm khỏi hóa đơn.")

        except ValidationError as e:
            return error_response(e.messages[0])

        except Exception:
            return error_response("Không thể xóa sản phẩm.",status=500,)

    return error_response("Method not allowed.", status=405,)
    
@login_required(login_url="login")
def checkout_order(request, order_id):
    if request.method != "POST": 
        return error_response("Method not allowed.", status=405,)

    try:
        order = get_object_or_404(SalesOrder,pk=order_id, employee=request.user,)

        process_checkout(order)

        new_order = get_or_create_draft_order(request.user)
        
        return success_response( data={ "next_order_id": new_order.id,
                                        "invoice_url": f"/sales/orders/{order.id}/print/",},
            message="Thanh toán hóa đơn thành công.")

    except ValidationError as e:
        return error_response(e.messages[0])

    except Exception:
        return error_response("Không thể thanh toán hóa đơn.",status=500,)

@login_required(login_url="login")
def cancel_order(request, order_id):
    if request.method != "POST":
        return error_response("Method not allowed.",status=405,)

    try:
        order = get_object_or_404(
            SalesOrder,
            pk=order_id,
        )

        if not request.user.is_owner:
            raise ValidationError("Chỉ Chủ Tiệm mới được hủy hóa đơn đã thanh toán.")

        process_cancel(order)

        return success_response(message="Hủy hóa đơn thành công.")

    except ValidationError as e:
        return error_response(e.messages[0])

    except Exception:
        return error_response("Không thể hủy hóa đơn.",status=500,)

@login_required(login_url="login")
def print_invoice(request, order_id):
    order = get_order(order_id)
    return render(request, "sales/invoice.html", {"order": order,},)


@login_required(login_url="login")
def orders_list(request):
    # Lấy tham số từ URL
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    
    # Lấy toàn bộ đơn hàng
    orders = SalesOrder.objects.select_related("employee").all().order_by("-created_at")

    # XỬ LÝ TÌM KIẾM CHUẨN XÁC
    if query:
        #
        code_value = query.upper().removeprefix("HDB").lstrip("0").strip()
        
        if code_value.isdigit():
            orders = orders.filter(pk=int(code_value))
        else:
            # Nếu là chuỗi chữ -> Tìm theo username, first_name hoặc last_name của nhân viên
            orders = orders.filter(
                Q(employee__first_name__icontains=query) |
                Q(employee__last_name__icontains=query)
            )

    # Xử lý lọc theo trạng thái
    valid_statuses = {value for value, _label in SalesOrder.Status.choices}
    if selected_status in valid_statuses:
        orders = orders.filter(status=selected_status)
    else:
        selected_status = ""

    return render(
        request,
        "sales/orders_management.html",
        {
            "orders": orders,
            "query": query,
            "selected_status": selected_status,
            "status_choices": SalesOrder.Status.choices,
        },
    )
    
@login_required(login_url="login")
def search_orders_list(request):
    # Lấy tham số từ URL
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    
    # Lấy toàn bộ đơn hàng, mặc định sắp xếp mới nhất lên đầu
    orders = SalesOrder.objects.select_related("employee").all().order_by("-created_at")

    # Xử lý tìm kiếm chuẩn xác
    if query:
        # Làm sạch chuỗi tìm kiếm mã hóa đơn 
        code_value = query.upper().replace(" ", "").removeprefix("HDB").lstrip("0")
        
        if code_value.isdigit():
            # Nếu người dùng nhập số -> Tìm chính xác theo ID (khóa chính) của hóa đơn
            orders = orders.filter(pk=int(code_value))
        else:
            # Nếu người dùng nhập chữ -> Tìm theo tên nhân viên (full_name hoặc username)
            orders = orders.filter(
                Q(employee__username__icontains=query) |
                Q(employee__full_name__icontains=query)
            )

    # Xử lý lọc theo trạng thái
    valid_statuses = {value for value, _label in SalesOrder.Status.choices}
    if selected_status in valid_statuses:
        orders = orders.filter(status=selected_status)
    else:
        selected_status = ""

    return render(
        request,"sales/orders_management.html",
        {
            "orders": orders,
            "query": query,
            "selected_status": selected_status,
            "status_choices": SalesOrder.Status.choices,
        },
    )
    