from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.db.models import (
    Case,
    F,
    IntegerField,
    Q,
    Value,
    When,
)

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from .models import Product, PurchaseReceipt, PurchaseItem
from .utils import process_search_products
from .forms import ProductForm
import json
from django.db import transaction
from django.urls import reverse

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

def product_search(request):
    if request.method != "GET":
        return error_response("Method not allowed.",status=405,)

    keyword = request.GET.get("q", "").strip()

    products = process_search_products(keyword)

    data = []

    for product in products:
        data.append({
            "id": product.id,
            "fabric_code": product.fabric_code,
            "name": product.name,
            "cost_price": product.cost_price,
            "selling_price": float(product.selling_price),
            "stock_quantity": product.stock_quantity,
        })

    return success_response(data=data)

@login_required(login_url="login")
def product_list(request):
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    stock_sort = request.GET.get("sort", "").strip()
    products = Product.objects.all()

    products = Product.objects.annotate(
        is_low_stock=Case(
            When(stock_quantity__lte=F('minimum_stock'), then=Value(0)), 
            default=Value(1),                                           
            output_field=IntegerField(),
        )
    )
    if query:
        filters = Q(name__icontains=query)
        code_value = query.upper().removeprefix("VAI-").removeprefix("VAI")
        if code_value.isdigit():
            filters |= Q(pk=int(code_value))
        products = products.filter(filters)

    valid_statuses = {value for value, _label in Product.Status.choices}
    if selected_status in valid_statuses:
        products = products.filter(status=selected_status)
    else:
        selected_status = ""

    if stock_sort not in {"stock_asc", "stock_desc"}:
        stock_sort = ""

    next_stock_sort = "stock_desc" if stock_sort == "stock_asc" else "stock_asc"
    stock_sort_params = {"sort": next_stock_sort}
    if query:
        stock_sort_params["q"] = query
    if selected_status:
        stock_sort_params["status"] = selected_status

    stock_order = "-stock_quantity" if stock_sort == "stock_desc" else "stock_quantity"

    products = products.annotate(
    low_stock_order=Case(
        When(
            stock_quantity__lte=F("minimum_stock"),
            then=Value(0),
        ),
        default=Value(1),
        output_field=IntegerField(),
    )
)

    if stock_sort:
        products = products.order_by("low_stock_order", stock_order, "pk")
    else:
        products = products.order_by("low_stock_order", "pk")

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products,
            "query": query,
            "selected_status": selected_status,
            "status_choices": Product.Status.choices,
            "stock_sort": stock_sort,
            "stock_sort_url": f"?{urlencode(stock_sort_params)}",
        },
    )


@login_required(login_url="login")
def product_detail(request, product_id):
    if not request.user.is_owner:
        return HttpResponseForbidden("Bạn không có quyền xem chi tiết hàng hóa.")
    
    product = get_object_or_404(Product.objects.prefetch_related("price_history"),pk=product_id,)
    
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if not form.is_valid():
            return error_response(message="Dữ liệu không hợp lệ.", status=400,)
        
        form.save()

        return success_response(message="Cập nhật mặt hàng thành công.")
        
    form = ProductForm(instance=product)

    return render(request, "inventory/product_detail.html",
        {   "product": product,
            "form": form,
            "price_history": product.price_history.order_by("created_at"),
        },
    )

@login_required(login_url="login")
def product_create(request):
    if not request.user.is_owner:
        return HttpResponseForbidden("Bạn không có quyền thực hiện thao tác này.")

    if request.method == "GET":
        return render(request, "inventory/product_create.html", {
            "form": ProductForm(),
        })

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            status = data.get("status", "active")

            if not name:
                return JsonResponse({"success": False, "message": "Vui lòng nhập tên mặt hàng!"})

            if Product.objects.filter(name__iexact=name).exists():
                return JsonResponse({
                    "success": False, 
                    "message": f"Mặt hàng mang tên '{name}' đã tồn tại trong kho!"
                })

            cost_price = Decimal(str(data.get("cost_price", 0)))
            profit_margin = Decimal(str(data.get("profit_margin", 0)))
            stock_quantity = Decimal(str(data.get("stock_quantity", 0)))
            minimum_stock = Decimal(str(data.get("minimum_stock", 0)))

            # Thống nhất kiểm tra Giá vốn phải > 0
            if cost_price <= 0:
                return JsonResponse({
                    "success": False, 
                    "message": "Giá vốn phải lớn hơn 0!"
                })

            if stock_quantity <= 0:
                return JsonResponse({
                    "success": False, 
                    "message": "Tồn kho phải lớn hơn 0!"
                })

            if minimum_stock <= 0:
                return JsonResponse({
                    "success": False, 
                    "message": "Tồn kho tối thiểu phải lớn hơn 0!"
                })

            if profit_margin < 0:
                return JsonResponse({
                    "success": False, 
                    "message": "% Lợi nhuận không được nhỏ hơn 0!"
                })

            product = Product.objects.create(
                name=name,
                cost_price=cost_price,
                profit_margin=profit_margin,
                stock_quantity=stock_quantity,
                minimum_stock=minimum_stock,
                status=status
            )

            return JsonResponse({
                "success": True, 
                "message": "Thêm mặt hàng mới thành công.",
                "product_id": product.id
            })

        except (InvalidOperation, TypeError, ValueError):
            return JsonResponse({
                "success": False, 
                "message": "Dữ liệu số nhập vào không hợp lệ!"
            })
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False, 
                "message": "Dữ liệu gửi lên không đúng định dạng JSON."
            })
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "message": f"Lỗi hệ thống: {str(e)}"
            })

    return JsonResponse({"success": False, "message": "Phương thức không được hỗ trợ."}, status=405)
    
@login_required
def purchase_list(request):
    query = request.GET.get("q", "").strip()
    
    purchases = PurchaseReceipt.objects.select_related("employee").all().order_by("-created_at")

    if query:
        code_value = query.upper().replace(" ", "").removeprefix("PN").lstrip("0")
        if code_value.isdigit():
            purchases = purchases.filter(pk=int(code_value))
        else:
            purchases = purchases.filter(supplier__name__icontains=query)

    return render(
        request,
        "inventory/purchase_management.html",
        {
            "purchases": purchases,
            "query": query,
        },
    )

@login_required
def search_purchase(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"success": True, "data": []})

    purchases = PurchaseReceipt.objects.select_related("employee").all().order_by("-created_at")
    
    code_value = query.upper().replace(" ", "").removeprefix("PN").lstrip("0")
    if code_value.isdigit():
        purchases = purchases.filter(pk=int(code_value))
    else:
        purchases = purchases.filter(supplier_name__icontains=query)

    data = []
    for p in purchases[:10]:
        data.append({
            "id": p.id,
            "purchase_code": p.purchase_code,
            "supplier_name": p.supplier_name or "Nhà cung cấp lẻ",
            "total_amount": float(p.total_amount),
            "created_at": p.created_at.strftime("%d/%m/%Y %H:%M"),
        })
    
    return JsonResponse({"success": True, "data": data})

@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(
        PurchaseReceipt.objects.select_related("employee").prefetch_related("items__product"),
        pk=purchase_id)

    return render(
        request, 
        "inventory/purchase_detail.html",
        {
            "purchase": purchase,
        }
    )

@login_required
def purchase_create(request):

    if request.method == "GET":
        return render(
            request,
            "inventory/purchase_create.html",
        )

    try:

        body = json.loads(request.body)

        supplier_name = body.get("supplier_name", "").strip()
        supplier_phone = body.get("supplier_phone", "").strip()
        items = body.get("items", [])

        if not items:
            return error_response("Phiếu nhập phải có ít nhất một mặt hàng.")

        with transaction.atomic():

            purchase = PurchaseReceipt.objects.create(
                employee=request.user,
                supplier_name=supplier_name,
                supplier_phone=supplier_phone,
            )

            total_amount = Decimal("0")

            for item in items:

                product_id = item.get("product_id")
                quantity = Decimal(str(item["quantity"]))
                unit_price = Decimal(str(item["unit_price"]))

                if product_id:

                    product = Product.objects.select_for_update().get(
                        pk=product_id
                    )

                    product.cost_price = unit_price

                else:

                    product = Product.objects.create(
                        name=item["name"],
                        cost_price=unit_price,
                    )

                product.stock_quantity += quantity
                product.save()

                purchase_item = PurchaseItem.objects.create(
                    receipt=purchase,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                )

                total_amount += purchase_item.subtotal

            purchase.total_amount = total_amount
            purchase.save(update_fields=["total_amount"])

        return success_response(
            data={
        "purchase_id": purchase.id,
        "redirect_url": reverse("inventory:purchase_list"),
    }, message="Lưu phiếu nhập thành công.",
)
    except Exception as e:
        return error_response(str(e))