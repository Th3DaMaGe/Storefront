from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from store.validators import validate_file_size
from django.core.files import File
from barcode import Code128
from barcode.writer import ImageWriter
import os
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from io import BytesIO
import barcode


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


## Note that the FK featured_product is dependent on Product.  Uses related_name ='+' which tells Django not to create a reverse relationship with Product with a collect
class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, related_name="+", blank=True
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Location(models.Model):
    WAREHOUSE_1 = "W1"
    WAREHOUSE_2 = "W2"
    STORAGE_AREA_1 = "S1"
    STORAGE_AREA_2 = "S2"
    STORAGE_AREA_3 = "S3"
    OFFICE_1 = "O1"
    OFFICE_2 = "O2"
    OFFICE_3 = "O3"

    VENUE_CHOICES = [
        (WAREHOUSE_1, "Warehouse 1"),
        (WAREHOUSE_2, "Warehouse 2"),
        (STORAGE_AREA_1, "Storage Room 1"),
        (STORAGE_AREA_2, "Storage Room 2"),
        (STORAGE_AREA_3, "Storage Room 3"),
        (OFFICE_1, "Office 1"),
        (OFFICE_2, "Office 2"),
        (OFFICE_3, "Office 3"),
    ]
    rank = models.CharField(max_length=5, default=1)
    shelf = models.CharField(max_length=5, default=1)
    tray = models.CharField(max_length=5, default=1)
    venue1 = models.CharField(max_length=2, choices=VENUE_CHOICES, default=WAREHOUSE_1)

    def __str__(self) -> str:
        """
        Returns a string representation of the Location object.

        This method is intended to provide a human-readable representation of the object,
        typically used for debugging and logging purposes.

        Returns:
            str: A string combining rank, shelf, and tray.
        """
        return f"Venue: {self.venue}, Rank: {self.rank}, Shelf: {self.shelf}, Tray: {self.tray}"

    class Meta:
        ordering = ["rank", "shelf", "tray"]


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    country_code = models.CharField(max_length=1, null=True)
    manufacturer_id = models.CharField(max_length=6, null=True)
    unit_price = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(1)]
    )
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name="products"
    )
    restock_value = models.IntegerField(default=20)
    # promotions = models.ManyToManyField(Promotion, blank=True)
    barcode = models.ImageField(upload_to="barcodes/", null=True, blank=True)
    numerical_barcode = models.CharField(
        max_length=100, null=True, blank=True
    )  # New field for numerical barcode
    barcode_thumbnail = ImageSpecField(
        source="barcode",
        processors=[ResizeToFill],
        format="PNG",
        options={"quality": 60},
    )
    model_number = models.CharField(max_length=16, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        EAN = barcode.get_barcode_class("ean13")
        ean = EAN(
            f"{self.country_code}{self.manufacturer_id}{self.model_number}",
            writer=ImageWriter(),
        )
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(
            f"{self.country_code}{self.manufacturer_id}{self.model_number}.png",
            File(buffer),
            save=False,
        )
        return super().save(*args, **kwargs)


class ProductInstance(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="instances"
    )
    serial_number = models.CharField(max_length=30, unique=True)
    sku = models.CharField(max_length=30)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "Out on Loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="a",
        help_text="Product Availability",
    )

    def __str__(self):
        return f"{self.product.title} - {self.serial_number}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    # image = models.ImageField(upload_to="store/images", validators=[validate_file_size])
    image = models.CharField(max_length=30, null=True, blank=True)


class Customer(models.Model):
    phone = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
        permissions = [("view_history", "Can View History")]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Complete"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    DELIVERY_STATUS_COMPLETE = "C"
    DELIVERY_STATUS_PENDING = "P"
    DELIVERY_STATUS_FAILED = "F"
    DELIVERY_STATUS_CHOICES = [
        (DELIVERY_STATUS_PENDING, "Pending"),
        (DELIVERY_STATUS_COMPLETE, "Complete"),
        (DELIVERY_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    delivery_status = models.CharField(
        max_length=1, choices=DELIVERY_STATUS_CHOICES, default=DELIVERY_STATUS_PENDING
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [("cancel_order", "Can cancel order")]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems"
    )
    quantity = models.PositiveSmallIntegerField()


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ## customer = models.OneToOneField(Customer, on_delete=models.CASCADE,primary_key=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.OneToOneField(settings.AUTH_USER_USER_MODEL, on_delete=models.CASCADE)
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Complete"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    DELIVERY_STATUS_COMPLETE = "C"
    DELIVERY_STATUS_PENDING = "P"
    DELIVERY_STATUS_FAILED = "F"
    DELIVERY_STATUS_CHOICES = [
        (DELIVERY_STATUS_PENDING, "Pending"),
        (DELIVERY_STATUS_COMPLETE, "Complete"),
        (DELIVERY_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    delivery_status = models.CharField(
        max_length=1, choices=DELIVERY_STATUS_CHOICES, default=DELIVERY_STATUS_PENDING
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, default=1)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        unique_together = [["cart", "product"]]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


class OrderStatusTextChoices(models.TextChoices):
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


class VendorStatusTextChoices(models.TextChoices):
    HIGH = "high", "High Priority"
    MEDIUM = "medium", "Medium Priority"
    LOW = "low", "Low Priority"


class VendorSpecialityTextChoices(models.TextChoices):
    COMPUTERS = "computers", "Computers"
    NETWORKING = "networking", "Networking"
    ELECTRICAL = "electrical", "Electrical"


class Vendor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=18)
    preference = models.CharField(
        max_length=18, choices=VendorStatusTextChoices.choices
    )
    speciality = models.CharField(
        max_length=18,
        choices=VendorSpecialityTextChoices.choices,
        default=VendorSpecialityTextChoices.COMPUTERS,
    )
