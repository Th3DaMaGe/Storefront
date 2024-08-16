from django.urls import path
from . import views
from django.core.cache import cache
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from django.views.generic import TemplateView

# URLConfs
urlpatterns = [
    path("", views.index),
    path("message_user/", views.message_user),
    path("hello/", views.say_hello),
    path("test/", views.say_test),
    path("email/", views.email),
    path("mail_attach/", views.attachments),
    path("template_email/", views.template_email),
    path("slow_request/", views.slow_request),
    path("hello_view/", TemplateView.as_view(template_name="hello.html")),
]
