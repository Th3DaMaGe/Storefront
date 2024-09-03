# management/commands/bulk_update_products.py

from django.core.management.base import BaseCommand
from store.models import Product
from django.core.files import File
import os
from barcode import Code128
from barcode.writer import ImageWriter
from django.conf import settings


class Command(BaseCommand):
    help = "Bulk update products with serial and model numbers and generate barcodes"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            # Update serial and model numbers
            product.serial_number = f"SN{product.id:06d}"
            product.model_number = f"MN{product.id:06d}"

            # Generate barcode
            barcode_value = str(product.id)
            barcode_filename = f"barcode_{product.id}"
            barcode_path = os.path.join(
                settings.MEDIA_ROOT, "barcodes", barcode_filename
            )
            if not os.path.exists(os.path.dirname(barcode_path)):
                os.makedirs(os.path.dirname(barcode_path))
            barcode = Code128(barcode_value, writer=ImageWriter())
            barcode.save(barcode_path)

            with open(f"{barcode_path}.png", "rb") as f:
                product.barcode.save(f"{barcode_filename}.png", File(f), save=False)

            product.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully updated products and generated barcodes")
        )
