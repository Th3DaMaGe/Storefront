from store.models import Product, ProductImage
from model_bakery.recipe import Recipe
from faker import factory, Faker
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings")
import django
django.setup()


myfake = Faker()

for k in range(50):
    products =Recipe(Product,
                     title=myfake.title(),
                     slug=myfake.slug(),
                     description=myfake.description(),
                     unit_price=myfake.unit_price(),
                     inventory=myfake.inventory(),
                     last_update=myfake.last_updated(),
                     collection=myfake.collection(),
                     restock_value=myfake.restock_value(),
                     serial_number=myfake.serial_number(),
                     model_number=myfake.model_number(),
                     )


