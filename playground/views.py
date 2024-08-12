from django.shortcuts import render
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage


def say_hello(request):
    try:
        send_mail("subject", "message", "perihelion@perihelion.com", ["bob@bobby.com"])
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "Mosh"})


def attachments(request):
    try:
        message = EmailMessage(
            "subject", "message", "perihelion@perihelion.com", ["bob@bobby.com"]
        )
        message.attach_file("playground/static/images/5bean.jpg")
        message.send()
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "Chikwanda"})


def email(request):
    try:
        mail_admins(
            "subject: mail_admins method",
            "message",
            html_message="perihelion@perihelion.com",
        )
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "User"})


def template_email(request):
    try:
        message = BaseEmailMessage(
            template_name="emails/email_template.html",
            context={"name": "Signed In User"},
        )
        message.send(["receipient@recipients.com"])
    except BadHeaderError:
        pass
    return render(request, "hello.html", {"name": "User"})
