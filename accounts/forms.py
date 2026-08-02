from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
import re

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Tài khoản",
        max_length=150,
        widget=forms.TextInput(attrs={
            "id": "username",
            "placeholder": "Tên đăng nhập",
            "autocomplete": "username"
        })
    )

    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            "id": "password",
            "placeholder": "Mật khẩu",
            "autocomplete": "current-password"
        })
    )

class ForgotPasswordForm(forms.Form):
    phone = forms.CharField(
        label="Số điện thoại",
        max_length=10,
        widget=forms.TextInput(attrs={
            "placeholder": "Nhập số điện thoại"
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                "Số điện thoại không tồn tại."
            )
        return phone


class VerifyPhoneForm(forms.Form):
    phone = forms.CharField(
        label="Số điện thoại",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            "placeholder": "Nhập số điện thoại"
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                "Số điện thoại không tồn tại."
            )
        return phone


class ResetPasswordForm(forms.Form):
    newPWD = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Nhập mật khẩu mới"
        })
    )

    confirmPWD = forms.CharField(
        label="Nhập lại mật khẩu",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Nhập lại mật khẩu"
        })
    )

    def clean_newPWD(self):
        password = self.cleaned_data.get("newPWD")
        if not password:
            return password

        if len(password) < 8:
            raise ValidationError("Mật khẩu phải có tối thiểu 8 ký tự!")

        if not re.search(r"[A-Z]", password):
            raise ValidationError("Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa (A-Z)!")

        if not re.search(r"\d", password):
            raise ValidationError("Mật khẩu phải chứa ít nhất 1 chữ số (0-9)!")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\\[\];'/`~]", password):
            raise ValidationError("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!, @, #, $, ...)!")
        return password

    def clean(self):
        cleaned_data = super().clean()
        new_pwd = cleaned_data.get("newPWD")
        confirm_pwd = cleaned_data.get("confirmPWD")

        if new_pwd and confirm_pwd and new_pwd != confirm_pwd:
            self.add_error("confirmPWD", "Mật khẩu xác nhận không khớp!")

        return cleaned_data
    
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu hiện tại"}),
        label="Mật khẩu hiện tại"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu mới"}),
        label="Mật khẩu mới"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu mới"}),
        label="Xác nhận mật khẩu mới"
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if self.user and not self.user.check_password(old_password):
            raise forms.ValidationError("Mật khẩu hiện tại không chính xác.")
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get("new_password")

        if len(new_password) < 8:
            raise forms.ValidationError("Mật khẩu mới phải có tối thiểu 8 ký tự.")

        if not re.search(r"[A-Z]", new_password):
            raise forms.ValidationError("Mật khẩu mới phải có ít nhất 1 chữ hoa.")

        if not re.search(r"\d", new_password):
            raise forms.ValidationError("Mật khẩu mới phải có ít nhất 1 chữ số.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
            raise forms.ValidationError("Mật khẩu mới phải có ít nhất 1 ký tự đặc biệt.")

        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", "Mật khẩu xác nhận không khớp.")

        return cleaned_data