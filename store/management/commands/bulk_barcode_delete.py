import os
from django.conf import settings
from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = "Delete stored barcode images from the database and file storage"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            # Delete barcode image file from storage
            # if product.barcode:
            #     barcode_path = product.barcode.path
            #     if os.path.exists(barcode_path):
            #         os.remove(barcode_path)

            # Clear the barcode field in the database
            product.barcode.delete(save=False)
            product.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully deleted barcode images from database and file storage"
            )
        )
