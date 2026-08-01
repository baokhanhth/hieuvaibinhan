from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Notification, User 
from django.contrib.auth import (authenticate,login,logout)
from django.views.decorators.cache import never_cache

import random

from .forms import (
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)

@never_cache
def logout_view(request):
    logout(request)

    response = redirect("login")

    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response

# @never_cache
# def login_view(request):
#     # if request.user.is_authenticated:
#     #     return redirect("sales:homepage")
    
#     form = LoginForm(request.POST or None)

#     if request.method == "POST" and form.is_valid():
#         user = authenticate(
#             request,
#             username=form.cleaned_data["username"],
#             password=form.cleaned_data["password"],
#         )

#         if user:
#             login(request, user)
#             return redirect("sales:homepage")

#         messages.error(request,"Sai tài khoản hoặc mật khẩu.")

#     response = render(request,"accounts/login.html",{"form": form,})

#     response["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response["Pragma"] = "no-cache"
#     response["Expires"] = "0"

#     return response

@never_cache
def login_view(request):
    # if request.user.is_authenticated:
    #     return redirect("sales:homepage")
    
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        if user:
            login(request, user)
            if user.is_owner:
                return redirect("sales:reports")
            else:
                return redirect("sales:homepage")

        messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")

    response = render(request, "accounts/login.html", {"form": form})

    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


def forgot_pwd(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        phone_number = form.cleaned_data["phone"]
        
        # Kiểm tra xem số điện thoại có tồn tại trong hệ thống hay không
        if User.objects.filter(phone=phone_number).exists():
            # Lưu số điện thoại vào session để trang reset_pwd biết đang đổi mật khẩu cho ai
            request.session["reset_phone"] = phone_number
            
            messages.success(request, "Xác thực thành công, vui lòng nhập mật khẩu mới.")
            return redirect("reset_pwd")
        else:
            form.add_error("phone", "Số điện thoại không tồn tại trong hệ thống. Vui lòng kiểm tra lại.")

    return render(request, "accounts/forgot_pwd.html", {"form": form})


def reset_pwd(request):
    form = ResetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        phone = request.session.get("phone")
        if phone is None:
            messages.error(request,"Phiên làm việc đã hết hạn.")
            return redirect("forgot_pwd")

        user = User.objects.get(phone=phone)
        user.set_password(form.cleaned_data["newPWD"])

        user.save()

        request.session.pop("phone", None)
        messages.success(request,"Đổi mật khẩu thành công.")
        return redirect("login")

    return render(request,"accounts/reset_pwd.html",{"form": form})

def process_create_low_stock_notification(product):

    users = User.objects.filter(is_active=True)

    for user in users:

        exists = Notification.objects.filter(
            receiver=user,
            product=product,
            type=Notification.Type.LOW_STOCK,
            is_resolved=False,
        ).exists()

        if exists:
            continue

        Notification.objects.create(
            receiver=user,
            product=product,
            type=Notification.Type.LOW_STOCK,
            title="Cảnh báo sắp hết hàng",
            message=(f'Loại vải "{product.name}" chỉ còn 'f'{product.stock_quantity} m. '"Vui lòng nhập thêm hàng."),
        )