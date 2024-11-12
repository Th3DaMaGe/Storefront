from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from store.models import (
    Product,
    Order,
    OrderItem,
    Collection,
    Cart,
    CartItem,
    Customer,
    ProductInstance,
)
from django.views import generic
from django.http import Http404
from django.views.generic import ListView
from .forms import LocationSearchForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import pytz
from datetime import datetime
from core.models import (
    User,
)
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import OrderForm, OrderItemForm, AddProductForm
from django.urls import reverse
from django.core.mail import send_mail
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from core.utils import scan_barcode
from django.forms import modelformset_factory
from core.forms import ProductForm


@csrf_exempt
def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response = JsonResponse(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
            response["Location"] = "/dashboard/"  # Redirect to dashboard page
            response.status_code = 302
            return response
        else:
            error_message = "Invalid credentials. Please try again."

    return render(request, "core/login.html", {"error_message": error_message})


@login_required
def profile_view(request):
    user = request.user

    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
    }

    if user.first_name and user.last_name:
        context["fullname"] = f"{user.first_name} {user.last_name}"
    else:
        context["fullname"] = None  # Set fullname to None if either attribute is null
    return render(request, "core/profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "core/product-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = self.object.images.all()
        return context

    def product_detail_view(request, primary_key):
        try:
            product = Product.objects.get(pk=primary_key)
        except Product.DoesNotExist:
            raise Http404("Product not in warehouses/store rooms")

        return render(request, "core/product-detail.html", context={"product": product})


def dashboard(request):
    user = request.user

    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
    }
    return render(request, "core/dashboard.html", context)


def product_list(request):
    user = request.user
    valid_sort_fields = ["title", "inventory", "last_update"]
    valid_orders = ["asc", "desc"]

    query = request.GET.get("q")
    sort_by = request.GET.get("sort_by", "title")  # Default sort by title
    order = request.GET.get("order", "asc")  # Default order is ascending

    # Validate sort_by and order parameters
    if sort_by not in valid_sort_fields:
        sort_by = "title"
    if order not in valid_orders:
        order = "asc"

    num_instances_available = ProductInstance.objects.filter(status__exact="a").count()
    num_instances_reserved = ProductInstance.objects.filter(status__exact="r").count()
    num_instances_on_loan = ProductInstance.objects.filter(status__exact="o").count()
    num_instances_maintainance = ProductInstance.objects.filter(
        status__exact="m"
    ).count()

    # Filter products based on query
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()

    # Apply sorting
    if order == "asc":
        products = products.order_by(sort_by)
    else:
        products = products.order_by(f"-{sort_by}")

    # Paginate the products
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "product_list": page_obj,
        "count": paginator.count,
        "num_instances_available": num_instances_available,
        "num_instances_reserved": num_instances_reserved,
        "num_instances_on_loan": num_instances_on_loan,
        "num_instances_maintainance": num_instances_maintainance,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "next": page_obj.has_next(),
        "previous": page_obj.has_previous(),
        "query": query,
        "sort_by": sort_by,
        "order": order,
        "username": user.username,
        "is_staff": user.is_staff,
    }
    return render(request, "core/product-list.html", context)


def product_list_view(request):
    user = request.user

    # Context dictionary to pass user information to the template
    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
    }

    # Fetch all products from the database
    products = Product.objects.all()
    num_instances_available = ProductInstance.objects.filter(status__exact="a").count()

    # Paginate the products list, showing 20 products per page
    paginator = Paginator(products, 20)

    # Get the current page number from the request
    page_number = request.GET.get("page")

    try:
        # Get the products for the current page
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    context["products"] = page_obj

    # Render the template with the products and user context
    return render(request, "core/product_list.html", context)


def index(request):
    return render(request, "core/index.html")


class RestockProducts(ListView):
    model = Product
    template_name = "core/restock-products.html"
    context_object_name = "products"

    # def get_queryset(self):
    #     return Product.objects.filter(inventory__lt=F("restock_value"))


def product_search(request):
    form = LocationSearchForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        rank = form.cleaned_data.get("rank")
        shelf = form.cleaned_data.get("shelf")
        tray = form.cleaned_data.get("tray")

        if rank:
            products = products.filter(location__rank=rank)
        if shelf:
            products = products.filter(location__shelf=shelf)
        if tray:
            products = products.filter(location__tray=tray)

    context = {
        "form": form,
        "products": products,
    }
    return render(request, "core/product-search.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        user = authenticate(username=request.user.username, password=old_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Old password is incorrect.")
            return redirect("change_password")

    return render(request, "core/change-password.html")


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def view_users(request):
    user = request.user
    user_details = {
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }

    if request.method == "POST":
        action = request.POST.get("action")
        user_ids = request.POST.getlist("user_ids")

        if action == "delete":
            User.objects.filter(id__in=user_ids).delete()
            return redirect("view-users")
        else:
            return HttpResponseForbidden(
                "You are not authorized to perform this action."
            )

    filter_by_staff = request.GET.get("filter_by_staff")
    if filter_by_staff == "staff":
        users = User.objects.filter(is_staff=True)
    elif filter_by_staff == "regular":
        users = User.objects.filter(is_staff=False)
    else:
        users = User.objects.all()

    now = datetime.now(pytz.utc)
    for user in users:
        if user.last_login:
            duration = now - user.last_login
            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            user.duration_last_login = (
                f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            )
        else:
            user.duration_last_login = None

    return render(
        request, "core/view-users.html", {"users": users, "user_details": user_details}
    )


def transactions_view(request):
    return render(request, "core/transactions.html")


def notifications_view(request):
    user = request.user

    # Context dictionary to pass user information to the template
    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
    }
    return render(request, "core/notifications.html", context)


def add_user(request):
    return render(request, "core/admin/add-user.html")


class UserForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False, label="Staff Status")
    is_superuser = forms.BooleanField(required=False, label="Admin Privileges")

    class Meta:
        model = User
        fields = [
            "username",
            "password1",
            "password2",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]


def users_crud_view(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data["is_staff"]
            user.is_superuser = form.cleaned_data["is_superuser"]
            user.save()
            return redirect("view-users")
    else:
        form = UserForm()
    return render(request, "core/admin/add-users.html", {"form": form})


def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("product-list")
    else:
        form = AddProductForm()
    return render(request, "core/admin/add-product.html", {"form": form})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order = Order.objects.get_or_create(user=request.user, is_active=True)
    order_item = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    print(order_item.quantity)
    order_item.save()
    return redirect("core:product_list")


def view_collections(request):
    user = request.user
    collections = Collection.objects.all()

    paginator = Paginator(collections, 20)  # Show 10 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "collections": page_obj,
        "username": user.username,
        "is_staff": user.is_staff,
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "next": page_obj.has_next(),
        "previous": page_obj.has_previous(),
    }
    return render(request, "core/view-collections.html", context)


def view_collection_products(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    products = collection.products.all()

    paginator = Paginator(products, 20)  # Show 10 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "collection": collection,
        "products": page_obj,
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "next": page_obj.has_next(),
        "previous": page_obj.has_previous(),
    }
    return render(request, "core/view-collection-products.html", context)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "core/order-success.html", {"order": order})


def create_order(request):
    OrderItemFormSet = inlineformset_factory(
        Order, OrderItem, form=OrderItemForm, extra=1
    )

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save()
            formset.instance = order
            formset.save()

            # Send email to the customer
            customer = order.customer
            send_order_email(customer, order)

            return redirect(reverse("order_success", kwargs={"order_id": order.id}))

    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()

    return render(
        request,
        "core/create-order.html",
        {
            "order_form": order_form,
            "formset": formset,
        },
    )


def send_order_email(customer, order):
    subject = f"Order Confirmation - Order #{order.id}"
    message = f"Dear {customer.first_name()},\n\nThank you for your order. Your order ID is {order.id}.\n\nBest regards,\nYour Company"
    from_email = "nameless.cleric@gmail.com"
    recipient_list = [customer.user.email]

    send_mail(subject, message, from_email, recipient_list)


class OrderListView(ListView):
    model = Order
    template_name = "core/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get("sort_by", "placed_at")
        if sort_by in ["payment_status", "delivery_status"]:
            queryset = queryset.order_by(sort_by)
        return queryset

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_orders = request.POST.getlist("selected_orders")

        if action == "delete" and selected_orders:
            orders_to_delete = Order.objects.filter(id__in=selected_orders)
            orders_to_delete.delete()
            messages.success(
                request, f"Deleted {orders_to_delete.count()} orders successfully."
            )

        return redirect("order-list")  # Redirect to the order list page


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = (
        order.items.all()
    )  # Assuming you have a related name 'items' for order items
    total_cost = sum(item.product.unit_price * item.quantity for item in order_items)

    return render(
        request,
        "core/order-detail.html",
        {
            "order": order,
            "order_items": order_items,
            "total_cost": total_cost,
        },
    )


def view_cart(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)

    context = {
        "cart": cart,
        "cart_items": cart.items.all(),
    }
    return render(request, "core/cart.html", context)


@login_required
def add_to_cart1(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create a Customer object for the user
    customer, created = Customer.objects.get_or_create(user=request.user)

    cart, created = Cart.objects.get_or_create(customer=customer)

    # Get quantity from request, default to 1 if not provided
    # Get quantity from POST data, default to 1 if not provided
    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += quantity
    cart_item.save()

    return redirect("product-list")


def user_type_pie_chart(request):
    # Query the database to get the count of staff and non-staff users
    staff_count = User.objects.filter(is_staff=True).count()
    non_staff_count = User.objects.filter(is_staff=False).count()

    # Data for the pie chart
    labels = ["Staff", "Non-Staff"]
    sizes = [staff_count, non_staff_count]
    colors = ["red", "blue"]

    # Create the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    # Return the pie chart as an HTTP response
    return HttpResponse(buffer, content_type="image/png")


def scan_product_barcode(request, product_id):
    product = Product.objects.get(pk=product_id)
    barcode_data = scan_barcode(product.barcode.path)
    return render(
        request,
        "product_detail.html",
        {"product": product, "barcode_data": barcode_data},
    )


def lookup_product_by_barcode(request):
    if request.method == "POST":
        barcode_image = request.FILES.get("barcode_image")
        if barcode_image:
            barcode_data = scan_barcode(barcode_image)
            if barcode_data:
                product = get_object_or_404(Product, numerical_barcode=barcode_data)
                return render(request, "product_detail.html", {"product": product})
            else:
                return render(
                    request,
                    "product_lookup.html",
                    {"error": "Barcode could not be read."},
                )
    return render(request, "core/product_lookup.html")


def receiving_view(request, extra_forms=5):  # Default to 5 extra forms
    ProductFormSet = modelformset_factory(Product, form=ProductForm, extra=extra_forms)
    if request.method == "POST":
        formset = ProductFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect("product-list")  # Replace with your success URL
    else:
        formset = ProductFormSet(queryset=Product.objects.none())

    return render(request, "core/receiving.html", {"formset": formset})
