# Generated by Django 4.2.15 on 2024-08-23 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0017_remove_product_expiry_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="barcode",
            field=models.ImageField(blank=True, null=True, upload_to="barcodes/"),
        ),
    ]
