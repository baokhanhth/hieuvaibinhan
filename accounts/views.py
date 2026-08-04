from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Notification, User 
from django.contrib.auth import (authenticate,login,logout, update_session_auth_hash)
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model

from .forms import ( ChangePasswordForm, LoginForm,ForgotPasswordForm,ResetPasswordForm,)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import re

User = get_user_model()

@never_cache
def logout_view(request):
    logout(request)
    
    response = redirect("login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


@never_cache
def login_view(request):
    initial_data = {}
    
    reset_username = request.session.pop("reset_username", None)
    if reset_username:
        initial_data["username"] = reset_username

    form = LoginForm(request.POST or None, initial=initial_data)

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


def reset_pwd(request):
    phone = request.session.get("reset_phone")
    
    if not phone:
        messages.error(request, "Phiên làm việc đã hết hạn. Vui lòng thử lại.")
        return redirect("forgot_pwd")

    form = ResetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            user = User.objects.get(phone=phone)
            user.set_password(form.cleaned_data["newPWD"])
            user.save()

            request.session["reset_username"] = user.username
            request.session.pop("reset_phone", None)
            
            messages.success(request, "Đổi mật khẩu thành công. Vui lòng đăng nhập lại.",)
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Không tìm thấy tài khoản tương ứng.")
            return redirect("forgot_pwd")

    return render(request, "accounts/reset_pwd.html", {"form": form})

def forgot_pwd(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        phone_number = form.cleaned_data["phone"]
        
        if User.objects.filter(phone=phone_number).exists():
            request.session["reset_phone"] = phone_number
            return redirect("reset_pwd")
        else:
            form.add_error("phone", "Số điện thoại không tồn tại trong hệ thống. Vui lòng kiểm tra lại.")

    return render(request, "accounts/forgot_pwd.html", {"form": form})


@login_required(login_url="login")
def change_pwd(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not request.user.check_password(old_password):
            return JsonResponse({"success": False, "message": "Mật khẩu hiện tại không chính xác."})

        if new_password != confirm_password:
            return JsonResponse({"success": False, "message": "Mật khẩu xác nhận không khớp."})

        if len(new_password) < 8:
            return JsonResponse({"success": False, "message": "Mật khẩu mới phải có ít nhất 8 ký tự."})

        if not re.search(r'[A-Z]', new_password):
            return JsonResponse({"success": False, "message": "Mật khẩu mới phải chứa ít nhất 1 chữ cái hoa (A-Z)."})

        if not re.search(r'[0-9]', new_password):
            return JsonResponse({"success": False, "message": "Mật khẩu mới phải chứa ít nhất 1 chữ số (0-9)."})

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            return JsonResponse({"success": False, "message": "Mật khẩu mới phải chứa ít nhất 1 ký tự đặc biệt."})

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        return JsonResponse({"success": True, "message": "Đổi mật khẩu thành công!"})

    return JsonResponse({"success": False, "message": "Phương thức không hợp lệ."}, status=405)


@login_required(login_url="login")
def mark_notifications_read(request):
    if request.method == "POST":
        from accounts.models import Notification
        Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)