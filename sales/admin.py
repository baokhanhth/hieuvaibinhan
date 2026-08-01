from django.contrib import admin
from .models import (
    SalesOrder,
    SalesOrderItem,
)

class SalesOrderItemInline(admin.TabularInline):
    """Giúp hiển thị các mặt hàng trong hóa đơn trực tiếp ngay trong trang chi tiết Hóa đơn"""
    model = SalesOrderItem
    extra = 0
    readonly_fields = ("subtotal",)

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_code",
        "employee",
        "discount",
        "total_amount",
        "final_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "employee__username",     )

    readonly_fields = (
        "order_code",
        "total_amount",
        "final_amount",
        "created_at",
        "completed_at",
        "updated_at",
    )

    inlines = [SalesOrderItemInline]


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "unit_price",
        "subtotal",
    )

    list_filter = (
        "product",
    )

    search_fields = (
        "order__id",
        "product__name",
    )