from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("hello/", views.say_hello),
    path("email/", views.email),
    path("mail_attach/", views.attachments),
    path("template_email/", views.template_email),
]
