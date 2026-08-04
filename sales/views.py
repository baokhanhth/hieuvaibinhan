import json
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from inventory.models import Product
from django.shortcuts import redirect
from .utils import process_search_order_list, success_response, error_response, process_reports_data
from .models import SalesOrder, SalesOrderItem
from django.db import transaction
from inventory.utils import process_search_products
from decimal import Decimal
from django.http import JsonResponse
from accounts.models import Notification, User
from django.core.paginator import Paginator

def get_orders():
    return (SalesOrder.objects.select_related("employee").order_by("-created_at"))

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

    # 1. Kiểm tra tồn kho đủ bán
    for item in items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock_quantity < item.quantity:
            raise ValidationError(f"Sản phẩm '{product.name}' không đủ tồn kho.")

    # Danh sách lưu các mặt hàng chạm hoặc dưới ngưỡng tồn tối thiểu
    low_stock_products = []
    active_users = list(User.objects.filter(is_active=True))

    # 2. Trừ tồn kho & kiểm tra ngưỡng tối thiểu
    for item in items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        product.stock_quantity -= item.quantity
        product.save(update_fields=["stock_quantity"])

        if product.stock_quantity <= product.minimum_stock:
            low_stock_products.append(product)

            for user in active_users:
                Notification.objects.create(
                    receiver=user,
                    product=product,
                    type=Notification.Type.LOW_STOCK,
                    title="Cảnh báo tồn kho thấp",
                    message=f"Sản phẩm '{product.name}' ({product.fabric_code}) hiện chỉ còn {product.stock_quantity:.1f}m (dưới/bằng ngưỡng tối thiểu {product.minimum_stock:.1f}m)."
                )

    _update_order_total(order)

    order.status = SalesOrder.Status.COMPLETED
    order.completed_at = timezone.now()
    order.save(update_fields=["status", "updated_at", "completed_at"])

    return order, low_stock_products

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
    filter_type = request.GET.get("filter", "30days")
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    data = process_reports_data(
        filter_type=filter_type,
        from_date_str=from_date_str,
        to_date_str=to_date_str
    )
    
    return JsonResponse(data)

    
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
        return error_response("Method not allowed.", status=405)

    try:
        order = get_object_or_404(SalesOrder, pk=order_id, employee=request.user)

        order, low_stock_products = process_checkout(order)
        new_order = get_or_create_draft_order(request.user)

        warnings = [
            f"Mặt hàng <b>{p.name}</b> ({p.fabric_code}) chỉ còn <b>{p.stock_quantity:.1f}m</b> (tồn tối thiểu: {p.minimum_stock:.1f}m)!"
            for p in low_stock_products
        ]

        return success_response(
            data={
                "next_order_id": new_order.id,
                "invoice_url": f"/sales/orders/{order.id}/print/",
                "low_stock_warnings": warnings  
            },
            message="Thanh toán hóa đơn thành công."
        )

    except ValidationError as e:
        return error_response(e.messages[0])
    except Exception as e:
        return error_response("Không thể thanh toán hóa đơn.", status=500)
    

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

    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()

    orders = process_search_order_list( keyword=query, status=selected_status)

    paginator = Paginator(orders, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "sales/orders_management.html",
        {
            "orders": page_obj,
            "page_obj": page_obj,
            "query": query,
            "selected_status": selected_status,
            "status_choices": SalesOrder.Status.choices,
        }
    )