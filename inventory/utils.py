from django.db.models import Q, Case, When, Value, IntegerField, F
from .models import Product, PurchaseReceipt
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
        {   "success": False,
            "message": message,
            "data": None,
        },
        status=status,
    )
    
def process_search_products(keyword="", status=""):
    products = Product.objects.annotate(
        low_stock_order=Case(
            When(
                status=Product.Status.ACTIVE,
                stock_quantity__lte=F("minimum_stock"),
                then=Value(0)
            ),
            default=Value(1),
            output_field=IntegerField(),
        )
    )

    if keyword:
        products = products.filter(
            Q(name__icontains=keyword) | Q(fabric_code__icontains=keyword)
        )

    if status:
        products = products.filter(status=status)

    return products

def process_search_purchase(query=""):
    purchases = PurchaseReceipt.objects.select_related("employee").all().order_by("-created_at")

    query = query.strip() if query else ""
    if query:
        raw_code = query.upper().replace(" ", "").removeprefix("PN")
        
        if raw_code.isdigit() and raw_code != "":
            purchases = purchases.filter(pk=int(raw_code))
        else:
            purchases = purchases.filter(
                Q(supplier_name__icontains=query) |
                Q(employee__full_name__icontains=query)            )

    return purchases