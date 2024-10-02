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
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    # serial_number = models.IntegerField(validators=[MinValueValidator(6)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name="products"
    )
    restock_value = models.IntegerField(default=20)
    promotions = models.ManyToManyField(Promotion, blank=True)
    barcode = models.ImageField(upload_to="barcodes/", null=True, blank=True)
    barcode_thumbnail = ImageSpecField(
        source="barcode",
        processors=[ResizeToFill],
        format="PNG",
        options={"quality": 60},
    )
    serial_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    model_number = models.CharField(max_length=30, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk": self.pk})

    # args=[str(self.id)]

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_barcode()

    def generate_barcode(self):
        barcode_value = str(self.id)  # Use the product ID or any unique value
        barcode_filename = f"barcode_{self.id}.png"
        barcode_path = os.path.join(settings.MEDIA_ROOT, "barcodes", barcode_filename)

        if not os.path.exists(os.path.dirname(barcode_path)):
            os.makedirs(os.path.dirname(barcode_path))

        barcode = Code128(barcode_value, writer=ImageWriter())
        barcode.save(barcode_path)

        with open(barcode_path, "rb") as f:
            self.barcode.save(barcode_filename, File(f), save=False)
        super().save(update_fields=["barcode"])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="store/images", validators=[validate_file_size])


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    # email = models.EmailField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
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

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
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
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ## customer = models.OneToOneField(Customer, on_delete=models.CASCADE,primary_key=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [["cart", "product"]]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
