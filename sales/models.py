from django.conf import settings
from django.db import models
from inventory.models import Product
from decimal import Decimal

class SalesOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Nháp"
        COMPLETED = "completed", "Đã thanh toán"
        CANCELLED = "cancelled", "Đã hủy"

    employee = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="sales_orders",verbose_name="Nhân viên")

    discount = models.DecimalField( max_digits=12,decimal_places=0,default=0,verbose_name="Giảm giá")
                                    
                                    

    total_amount = models.DecimalField( max_digits=12,decimal_places=0,default=0,verbose_name="Tổng tiền")
                                                 
    final_amount = models.DecimalField( max_digits=12,decimal_places=0,default=0,verbose_name="Thành tiền")

    status = models.CharField(  max_length=20,choices=Status.choices,default=Status.DRAFT,db_index=True,verbose_name="Trạng thái")

    created_at = models.DateTimeField( auto_now_add=True, verbose_name="Ngày lập")

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày thanh toán")
    updated_at = models.DateTimeField( auto_now=True,verbose_name="Ngày cập nhật")
    note = models.TextField(blank=True, default="", verbose_name="Ghi chú")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Hóa đơn bán"
        verbose_name_plural = "Hóa đơn bán"

    @property
    def order_code(self):
        return f"HDB{self.pk:07d}" if self.pk else "HDBM"

    def __str__(self):
        return self.order_code


class SalesOrderItem(models.Model):
    order = models.ForeignKey( SalesOrder, on_delete=models.CASCADE, related_name="items",verbose_name="Hóa đơn")

    product = models.ForeignKey(Product, on_delete=models.PROTECT,related_name="sales_items",verbose_name="Sản phẩm")

    quantity = models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Số lượng (mét)")

    unit_price = models.DecimalField( max_digits=12, decimal_places=0,verbose_name="Đơn giá")
    subtotal = models.DecimalField(max_digits=12,decimal_places=0,editable=False,verbose_name="Thành tiền")

    class Meta:
        ordering = ["id"]
        verbose_name = "Chi tiết hóa đơn"
        verbose_name_plural = "Chi tiết hóa đơn"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order} - {self.product}"