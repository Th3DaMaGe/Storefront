import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Collection, ProductImage, ProductInstance


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
            elif collection.title == "Networkking Equipment":
                brand = "Generic"
                suffix = "Network"
            elif collection.title == "Accessories":
                brand = "Generic"
                suffix = "Accessory"
            elif collection.title == "Tools":
                brand = "Generic"
                suffix = "Tool"
            elif collection.title == "Electrical Equipment":
                brand = "Generic"
                suffix = "Electrical"

            title = f"{brand} {suffix}"
            last_update = timezone.now() - timedelta(days=random.randint(1, 300))

            # Generate a consistent model number based on brand and suffix

            product = Product.objects.create(
                title=title,
                slug=fake.slug(),
                description=fake.text(),
                unit_price=random.uniform(100, 1000),
                last_update=last_update,
                collection=collection,
                restock_value=random.randint(10, 50),
                manufacturer_id=f"{random.randint(0, 999999):06}",  # Ensures 6 digits,
                country_code=f"{random.randint(0, 9):01}",  # Ensures 1 digit,
                model_number=f"{random.randint(0, 99999):05}",  # Ensures 5 digits
            )

            # Create ProductInstance objects
            for _ in range(random.randint(1, 20)):  # Random number of instances
                ProductInstance.objects.create(
                    product=product,
                    serial_number=fake.unique.uuid4(),
                    sku=fake.unique.uuid4(),
                    status=random.choice(
                        ["m", "o", "a", "r"]
                    ),  # Randomly select a status
                )

            # Add product images
            image_url = "https://picsum.photos/seed/picsum/200/300"
            ProductImage.objects.create(product=product, image=image_url)

        self.stdout.write(self.style.SUCCESS("Successfully generated dummy data"))
