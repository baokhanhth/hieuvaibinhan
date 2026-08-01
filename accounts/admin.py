from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    
    # Hiển thị các cột này ra ngoài danh sách User
    list_display = (
        "username",
        "full_name",
        "phone",
        "role",          # Cột hiển thị vai trò
        "is_active",
        "is_staff",
    )
    
    # Bộ lọc bên phải màn hình danh sách
    list_filter = (
        "role",          # Cho phép lọc theo Chủ cửa hàng / Nhân viên
        "is_active",
        "is_staff",
    )
    
    search_fields = (
        "username",
        "full_name",
        "phone",
    )
    
    ordering = ("full_name",)

    # Giao diện khi bấm vào xem/sửa chi tiết một User có sẵn
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {"fields": ("full_name", "phone", "role")}), # Đã đưa 'role' vào đây
        ("Phân quyền & Trạng thái", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Thời gian quan trọng", {"fields": ("last_login", "date_joined")}),
    )
    
    # Giao diện khi bấm nút "Thêm người dùng" (Add user)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "full_name", "phone", "role", "password1", "password2"), # Đã có 'role' để gán ngay khi tạo
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "receiver",
        "product",
        "type",
        "is_read",
        "is_resolved",
        "created_at",
    )
    list_filter = ("type", "is_read", "is_resolved", "created_at")
    search_fields = ("title", "message", "receiver__username", "receiver__full_name")
    readonly_fields = ("created_at",)