from django.contrib.auth.models import AbstractUser
from django.db import models
from inventory.models import Product
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    first_name = None
    last_name = None

    class Role(models.TextChoices):
        OWNER = "OWNER", "Chủ cửa hàng"
        EMPLOYEE = "EMPLOYEE", "Nhân viên"
        
    username = models.CharField(max_length=50,unique=True,verbose_name="Tên đăng nhập")

    full_name = models.CharField(max_length=100,verbose_name="Họ và tên")

    phone = models.CharField(max_length=10,unique=True,verbose_name="Số điện thoại")

    role = models.CharField( max_length=20, choices=Role.choices, default=Role.EMPLOYEE, verbose_name="Vai trò")
    
    is_active = models.BooleanField(default=True,verbose_name="Đang hoạt động")

    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Ngày tạo")

    updated_at = models.DateTimeField(auto_now=True,verbose_name="Ngày cập nhật")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name", "phone"]
    
    class Meta:
        db_table = "users"
        ordering = ["full_name"]
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        
    def __str__(self):
        return self.full_name
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE
    
class Notification(models.Model):

    class Type(models.TextChoices):
        LOW_STOCK = "LOW_STOCK", "Sắp hết hàng"

    receiver = models.ForeignKey(   settings.AUTH_USER_MODEL, 
                                    on_delete=models.CASCADE,
                                    related_name="notifications",
                                    verbose_name="Người nhận",
                                )

    product = models.ForeignKey( Product, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True, verbose_name="Hàng hóa",)

    type = models.CharField( max_length=30, choices=Type.choices, verbose_name="Loại thông báo",)

    title = models.CharField( max_length=255, verbose_name="Tiêu đề",)

    message = models.TextField(verbose_name="Nội dung",)

    is_read = models.BooleanField( default=False, verbose_name="Đã đọc",)

    is_resolved = models.BooleanField(default=False, verbose_name="Đã xử lý",)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo",)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"

    def __str__(self):
        return self.title