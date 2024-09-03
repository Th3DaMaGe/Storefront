from django.urls import path
from .views import login_view, profile_view, logout_view, product_list, index, haploid
from .views import dashboard, ProductDetailView, RestockProducts

# URLConf
urlpatterns = [
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("product/<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("product-list/", product_list, name="product-list"),
    path("haploid/", haploid, name="haploid"),
    path("restock-products/", RestockProducts.as_view(), name="restock-products"),
]
