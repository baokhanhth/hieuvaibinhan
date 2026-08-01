from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path("forgot-password/", views.forgot_pwd, name="forgot_pwd"),
    path("reset-password/", views.reset_pwd, name="reset_pwd"),
    path("logout/", views.logout_view, name="logout"),
]