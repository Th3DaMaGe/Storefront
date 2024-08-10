from django.shortcuts import render
from django.core.mail import send_mail, mail_admins, BadHeaderError


def say_hello(request):
    try:
        send_mail("subject", "message", "perihelion@perihelion.com", ["bob@bobby.com"])
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "Mosh"})


def email(request):
    try:
        mail_admins(
            "subject", "message", "perihelion@perihelion.com", ["bob@bobby.com"]
        )
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "User"})
