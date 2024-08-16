from django.shortcuts import render
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from django.http import HttpResponse
from store.models import Product, ProductImage
from templated_mail.mail import BaseEmailMessage
from twilio.rest import Client
from rest_framework.views import APIView
from storefront.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
import requests
import logging

logger = logging.getLogger(__name__)


order_details = {
    "amount": "5kg",
    "item": "Tomatoes",
    "date_of_delivery": "03/04/2024",
    "address": "This is a test address",
}


def message_user(request):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    if request.method == "POST":
        user_whatsapp_number = request.POST["user_number"]

        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body="Your {} order of {} has shipped and should be delivered on {}. Details: {}.  Note: This is ".format(
                order_details["amount"],
                order_details["item"],
                order_details["date_of_delivery"],
                order_details["address"],
            ),
            to="whatsapp:+{}".format(user_whatsapp_number),
        )

        print(user_whatsapp_number)
        print(message.sid)
        return HttpResponse("Great! Expect a message...")

    return render(request, "whatsapp_user_test.html")
    pass


def index(request):
    # num_products = Product.objects.all().count()
    # context = {"num_products": num_products}
    return render(request, "index.html", {"name": "TheNamelessOne"})


def say_test(request):
    return render(request, "hello.html", {"name": "Mosh"})


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


def slow_request(request):
    requests.get("https://httpbin.org/delay/2")
    return render(request, "hello.html", {"name": "Chikwanda"})


class HelloView(APIView):
    def get(self, request):
        try:
            logger.info("Calling httpbin")
            response = requests.get("https://httpbin.org/delay/5")
            logger.info("Response received")
            data = response.json()
        except request.ConnectionError:
            logger.critical("Connection error: Site offline")
        return render(request, "hello.html", {"name": "Chikwanda"})
