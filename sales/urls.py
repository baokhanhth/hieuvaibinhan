from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [

    path("", views.homepage, name="homepage"),
    path("products/search-sale/", views.product_search_sale, name="product_search_sale",),
    
    path("orders/", views.orders, name="orders"),
    path("orders/new-draft/", views.new_draft, name="new_draft",),
    
    path("orders/list/", views.orders_list, name="orders_management"),
    path("orders/search-order/", views.search_orders_list, name="search_orders_list"),
    
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/data/",views.order_data,name="order_data",),
    path("orders/<int:order_id>/delete/",views.delete_order,name="delete_order",),


    path("orders/<int:order_id>/items/", views.order_items, name="order_items",),
    path("orders/<int:order_id>/items/<int:item_id>/", views.order_item_detail, name="order_item_detail",),
    path("orders/<int:order_id>/checkout/", views.checkout_order, name="checkout_order",),
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order",),
    path("orders/<int:order_id>/print/", views.print_invoice, name="print_invoice",),
    
    path("reports/", views.reports, name="reports"),
    path("reports/data/", views.reports_data, name="reports_data"),
]