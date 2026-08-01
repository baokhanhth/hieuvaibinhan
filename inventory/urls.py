from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("create/", views.product_create, name="product_create"),
    path("product-detail/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/search/", views.product_search, name="product_search"),
    # path("products/management/", views.purchase_management, name="purchase_management"),
    
    path("purchase/", views.purchase_list, name="purchase_list",),
    path("purchase/search/", views.search_purchase, name="search_purchase",),
    path("purchase/create/", views.purchase_create, name="purchase_create",),
    path("purchase/<int:purchase_id>/",views.purchase_detail,name="purchase_detail",),
]
