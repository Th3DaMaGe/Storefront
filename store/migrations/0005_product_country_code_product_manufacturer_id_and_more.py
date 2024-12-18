# Generated by Django 4.2.16 on 2024-11-14 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_vendor_speciality"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="country_code",
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="manufacturer_id",
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
