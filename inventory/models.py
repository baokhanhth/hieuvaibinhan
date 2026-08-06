from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import models
from decimal import Decimal

# Create your models here.
class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Còn bán"
        INACTIVE = "inactive", "Ngừng kinh doanh"

    name = models.CharField(max_length=200,unique=True,verbose_name="Tên vải"    )

    cost_price = models.DecimalField(max_digits=12,decimal_places=0,default=0, verbose_name="Giá vốn"    )

    selling_price = models.DecimalField(max_digits=12,decimal_places=0,default=0,verbose_name="Giá bán")

    stock_quantity = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal("0.00"),verbose_name="Tồn kho (mét)")
    
    minimum_stock = models.DecimalField(max_digits=10,decimal_places=2,default=5,verbose_name="Tồn kho tối thiểu")
    
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.ACTIVE, verbose_name="Trạng thái")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    
    profit_margin = models.DecimalField(max_digits=5,decimal_places=2,default=Decimal("0.00"), verbose_name="Tỷ lệ lợi nhuận (%)")

    @property
    def fabric_code(self):
        return f"VAI{self.pk:06d}" if self.pk else "VAI"

    def save(self, *args, **kwargs):
        old_cost_price = None

        if self.pk:
            old_cost_price = Product.objects.get(pk=self.pk).cost_price

        if self.cost_price is not None and self.profit_margin is not None:
            margin_ratio = self.profit_margin / Decimal("100")
            self.selling_price = (self.cost_price * (Decimal("1.00") + margin_ratio)).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )

        super().save(*args, **kwargs)

        if old_cost_price is None or old_cost_price != self.cost_price:
            ProductPriceHistory.objects.create(
                product=self,
                cost_price=self.cost_price,
                selling_price=self.selling_price,
            )
        
    class Meta:
        verbose_name = "Mặt hàng"
        verbose_name_plural = "Mặt hàng"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class ProductPriceHistory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="Sản phẩm",
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Giá vốn",
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Giá bán",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời điểm áp dụng",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lịch sử giá"
        verbose_name_plural = "Lịch sử giá"

class PurchaseReceipt(models.Model):

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchase_receipts",verbose_name="Người lập"
    )

    supplier_name = models.CharField( max_length=200,verbose_name="Tên nhà cung cấp")

    supplier_phone = models.CharField(max_length=15,blank=True,verbose_name="SĐT nhà cung cấp")

    total_amount = models.DecimalField( max_digits=14, decimal_places=0,default=0,verbose_name="Tổng tiền")

    created_at = models.DateTimeField( auto_now_add=True,verbose_name="Ngày nhập")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phiếu nhập"
        verbose_name_plural = "Phiếu nhập"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PN{self.pk:05d}"
    @property
    def purchase_code(self):
        return f"PN{self.pk:05d}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        return total
    
class PurchaseItem(models.Model):

    receipt = models.ForeignKey( PurchaseReceipt,on_delete=models.CASCADE,related_name="items",verbose_name="Phiếu nhập"
    )

    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="purchase_items",verbose_name="Vải")

    quantity = models.DecimalField( max_digits=10,decimal_places=2,verbose_name="Số lượng (m)")

    unit_price = models.DecimalField( max_digits=12,decimal_places=0,verbose_name="Giá nhập")

    subtotal = models.DecimalField(max_digits=14, decimal_places=0,editable=False, verbose_name="Thành tiền")

    class Meta:
        verbose_name = "Chi tiết phiếu nhập"
        verbose_name_plural = "Chi tiết phiếu nhập"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity} m)"
