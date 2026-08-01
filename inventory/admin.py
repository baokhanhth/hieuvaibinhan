from django.contrib import admin
from .models import (
    Product,
    ProductPriceHistory,
    PurchaseReceipt,
    PurchaseItem,
)

class ProductPriceHistoryInline(admin.TabularInline):
    """Hiển thị lịch sử thay đổi giá trực tiếp ngay trong trang chi tiết Sản phẩm"""
    model = ProductPriceHistory
    extra = 0
    readonly_fields = ("cost_price", "selling_price", "created_at")
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "fabric_code",
        "name",
        "cost_price",
        "profit_margin",
        "selling_price",
        "stock_quantity",
        "minimum_stock",
        "status",
    )
    
    list_filter = (
        "status",
    )
    
    search_fields = (
        "name",
    )
    
    readonly_fields = (
        "selling_price",
        "created_at",
        "updated_at",
    )
    
    inlines = [ProductPriceHistoryInline]


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "cost_price",
        "selling_price",
        "created_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "product__name",
    )


class PurchaseItemInline(admin.TabularInline):
    """Hiển thị các dòng chi tiết vải nhập kho ngay trong trang Phiếu nhập"""
    model = PurchaseItem
    extra = 1


@admin.register(PurchaseReceipt)
class PurchaseReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_code",
        "employee",
        "supplier_name",
        "supplier_phone",
        "total_amount",
        "created_at",
    )
    
    list_filter = (
        "created_at",
        "supplier_name",
    )
    
    search_fields = (
        "supplier_name",
        "supplier_phone",
    )
    
    readonly_fields = (
        "total_amount",
        "created_at",
        "updated_at",
    )
    
    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "receipt",
        "product",
        "quantity",
        "unit_price",
        "subtotal",
    )
    
    list_filter = (
        "product",
    )
    
    search_fields = (
        "receipt__id",
        "product__name",
    )