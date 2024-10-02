from store.models import Order, OrderItem, Product, Collection
from django import forms


class LocationSearchForm(forms.Form):
    rank = forms.CharField(max_length=30, required=False)
    shelf = forms.CharField(max_length=30, required=False)
    tray = forms.CharField(max_length=30, required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "payment_status"]


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "description",
            "unit_price",
            "inventory",
            "collection",
            "restock_value",
            # "barcode",
            "serial_number",
            "model_number",
        ]

    title = forms.CharField(label="Product Title")
    slug = forms.SlugField(label="Product Slug")
    description = forms.CharField(widget=forms.Textarea, label="Product Description")
    unit_price = forms.DecimalField(label="Unit Price")
    inventory = forms.IntegerField(label="Inventory")
    collection = forms.ModelChoiceField(queryset=Collection.objects.all(), label="Collection")
    restock_value = forms.IntegerField(label="Restock Value")
    # barcode = forms.CharField(label="Barcode")
    serial_number = forms.CharField(label="Serial Number")
    model_number = forms.CharField(label="Model Number")
