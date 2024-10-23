import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Collection, ProductImage


class Command(BaseCommand):
    help = "Generate dummy data for Products and Collections"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Define collections
        collections = [
            "Computers - Laptops",
            "Computers - Servers",
            "Computers - AIO",
            "Computers - Desktops",
            "Monitors",
            "Networking Equipment",
            "Accessories",
            "Tools",
            "Electrical Equipment",
        ]

        # Create collections
        collection_objects = {}
        for collection_title in collections:
            collection, created = Collection.objects.get_or_create(
                title=collection_title
            )
            collection_objects[collection_title] = collection

        # Define brands and suffixes
        laptop_brands = ["HP", "ASUS", "LENOVO", "GIGABYTE", "TOSHIBA"]
        desktop_brands = ["HP", "ASUS", "LENOVO", "GIGABYTE", "TOSHIBA"]
        server_brands = ["HP", "ASUS", "LENOVO", "GIGABYTE", "TOSHIBA"]
        monitor_brands = ["Sony", "Toshiba", "LENOVO", "GIGABYTE", "FUJITSU"]

        laptop_suffixes = ["13 inch", "15 inch", "17 inch Workstation"]
        desktop_suffixes = ["Gaming", "Office", "Home"]
        server_suffixes = ["Rack", "Tower", "Blade"]
        monitor_suffixes = ["15 inch", "17 inch", "21 inch"]

        # Generate products
        for _ in range(100):  # Adjust the range for the number of products you want
            collection = random.choice(list(collection_objects.values()))
            brand = "Generic"
            suffix = "Product"

            if collection.title == "Computers - Laptops":
                brand = random.choice(laptop_brands)
                suffix = random.choice(laptop_suffixes)
            elif collection.title == "Computers - Desktops":
                brand = random.choice(desktop_brands)
                suffix = random.choice(desktop_suffixes)
            elif collection.title == "Computers - Servers":
                brand = random.choice(server_brands)
                suffix = random.choice(server_suffixes)
            elif collection.title == "Monitors":
                brand = random.choice(monitor_brands)
                suffix = random.choice(monitor_suffixes)

            title = f"{brand} {suffix}"
            last_update = timezone.now() - timedelta(days=random.randint(1, 300))

            product = Product.objects.create(
                title=title,
                slug=fake.slug(),
                description=fake.text(),
                unit_price=random.uniform(100, 1000),
                inventory=random.randint(1, 100),
                last_update=last_update,
                collection=collection,
                restock_value=random.randint(10, 50),
                serial_number=fake.unique.uuid4(),
                model_number=fake.unique.uuid4(),
            )

            # Add product images
            image_url = ""
            if collection.title == "Computers - Laptops":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Computers - Servers":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Computers - AIO":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Computers - Desktops":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Monitors":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Networking Equipment":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Accessories":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Tools":
                image_url = "https://picsum.photos/seed/picsum/200/300"
            elif collection.title == "Electrical Equipment":
                image_url = "https://picsum.photos/seed/picsum/200/300"

            ProductImage.objects.create(product=product, image=image_url)

        self.stdout.write(self.style.SUCCESS("Successfully generated dummy data"))
