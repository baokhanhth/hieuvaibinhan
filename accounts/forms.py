from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


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
        password = self.cleaned_data["newPWD"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()

        new_pwd = cleaned_data.get("newPWD")
        confirm_pwd = cleaned_data.get("confirmPWD")

        if new_pwd and confirm_pwd and new_pwd != confirm_pwd:
            self.add_error(
                "confirmPWD",
                "Mật khẩu nhập lại không khớp."
            )
        return cleaned_data