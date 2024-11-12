from django.urls import path
from core.views import (
    login_view,
    profile_view,
    logout_view,
    product_list,
    index,
    product_search,
    change_password,
    view_users,
    transactions_view,
    notifications_view,
    users_crud_view,
    add_product,
    view_collections,
    view_collection_products,
    add_to_cart,
    create_order,
    order_success,
    OrderListView,
    order_detail,
    add_to_cart1,
    view_cart,
    user_type_pie_chart,scan_product_barcode,
    lookup_product_by_barcode
    
)
from core.views import dashboard, ProductDetailView, RestockProducts

# URLConf
# This code defines views and functions for a Django web application, handling user authentication, product browsing, cart management, and administrative tasks.
urlpatterns = [
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("product/<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("product-list/", product_list, name="product-list"),
    path("restock-products/", RestockProducts.as_view(), name="restock-products"),
    path("product-search/", product_search, name="product-search"),
    path("change-password/", change_password, name="change-password"),
    path("view-users/", view_users, name="view-users"),
    path("view-collection/", view_collections, name="view-collection"),
    path(
        "view_collection/<int:collection_id>",
        view_collection_products,
        name="view-collection-products",
    ),
    path("create-order/", create_order, name="create-order"),
    path("transactions/", transactions_view, name="transactions"),
    path("notifications/", notifications_view, name="notifications"),
    path("ims-admin/add-users/", users_crud_view, name="users-crud-view"),
    path("add-cart/<int:product_id>", add_to_cart, name="add-order"),
    path("ims-admin/add-product/", add_product, name="add-product"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("order/<int:order_id>/", order_detail, name="order_detail"),
    path("add-to-cart1/<int:product_id>/", add_to_cart1, name="add_to_cart1"),
    path("view-cart/", view_cart, name="view-cart"),
    path("user-type/", user_type_pie_chart, name="user_type_pie_chart"),
    path('product-lookup/', lookup_product_by_barcode, name='lookup-product-by-barcode'),
    path('product/<int:product_id>/scan/', scan_product_barcode, name='scan-product-barcode'),
]
