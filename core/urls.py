from django.views.generic import TemplateView
from django.urls import path
from .views import login_view, profile_view, logout_view

# URLConf
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html")),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
]
