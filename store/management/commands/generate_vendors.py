import os
import django
from faker import Faker
from store.models import Vendor  # Replace 'your_app' with the name of your Django app
from store.models import VendorSpecialityTextChoices
from store.models import VendorStatusTextChoices
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate dummy data for Products and Collections"

    def handle(self, *args, **kwargs):
        # Initialize Faker
        fake = Faker()

        # Generate and save 20 fake vendors
        for _ in range(20):
            vendor = Vendor(
                name=fake.company(),
                address=fake.address(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                preference=fake.random_element(
                    elements=[choice[0] for choice in VendorStatusTextChoices.choices]
                ),
                speciality=fake.random_element(
                    elements=[choice[0] for choice in VendorSpecialityTextChoices.choices]
                ),
            )
            vendor.save()

        print("20 fake vendors have been created.")
