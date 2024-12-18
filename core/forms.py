from store.models import Order, OrderItem, Product, Collection
from django import forms
from django.forms import inlineformset_factory


class LocationSearchForm(forms.Form):
    rank = forms.CharField(max_length=30, required=False)
    shelf = forms.CharField(max_length=30, required=False)
    tray = forms.CharField(max_length=30, required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "payment_status"]


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
)


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
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.all(), label="Collection"
    )
    restock_value = forms.IntegerField(label="Restock Value")
    # barcode = forms.CharField(label="Barcode")
    serial_number = forms.CharField(label="Serial Number")
    model_number = forms.CharField(label="Model Number")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "description",
            "unit_price",
            "collection",
            "restock_value",
            "model_number",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}),
            "slug": forms.TextInput(attrs={"class": "form-input w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}),
            "description": forms.Textarea(
                attrs={"class": "form-textarea w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}
            ),
            "unit_price": forms.NumberInput(
                attrs={"class": "form-input w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}
            ),
            "collection": forms.Select(
                attrs={"class": "form-select w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}
            ),
            "restock_value": forms.NumberInput(
                attrs={"class": "form-input w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}
            ),
            "model_number": forms.TextInput(
                attrs={"class": "form-input w-full text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded"}
            ),
        }
