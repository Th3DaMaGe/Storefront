from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<20", "Low < 20")]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<20":
            return queryset.filter(inventory__lt=20)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ["thumbnail"]

    def thumbnail(self, instance):
        if instance.image.name != "":
            return format_html(f'<img src="{instance.image.url}" class="thumbnail"/>')
        return ""


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    # actions = ["clear_inventory"]
    inlines = [ProductImageInline]
    list_display = [
        "title",
        "unit_price",
        # "inventory_status",
        "collection_title",
        "barcode",
        "barcode_thumbnail_tag",
        "restock_value",
    ]
    list_editable = ["unit_price", "restock_value"]
    list_filter = ["collection", "last_update"]
    list_per_page = 20
    list_select_related = ["collection"]
    search_fields = ["title"]

    def collection_title(self, product):
        return product.collection.title

    def barcode_thumbnail_tag(self, obj):
        if obj.barcode:
            return format_html(
                '<img src="{}" width="100" height="100" />', obj.barcode.url
            )
        return "No barcode. 🥺"

    barcode_thumbnail_tag.short_description = "Bar Code Thumbnail"

    # @admin.display(ordering="inventory")
    # def inventory_status(self, product):
    #     if product.inventory < 10:
    #         return "Less Than 10 Units Left"
    #     elif product.inventory < 50:
    #         return product.inventory
    #     return "OK Inventory > 50 Units Left"

    # @admin.action(description="Clear inventory")
    # def clear_inventory(self, request, queryset):
    #     updated_count = queryset.update(inventory=0)
    #     self.message_user(
    #         request,
    #         f"{updated_count} products were successfully updated.",
    #         messages.ERROR,
    #     )

    class Media:
        css = {"all": ["store/styles.css"]}


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["featured_product"]
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html(
            '<a href="{}">{} Products</a>', url, collection.products_count
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "orders"]
    list_per_page = 10
    ordering = ["user__first_name", "user__last_name"]
    list_select_related = ["user"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 100
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer"]
