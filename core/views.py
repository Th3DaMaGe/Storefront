from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from store.models import Product
from django.views import generic
from django.http import Http404
import requests
from django.views.generic import ListView
from django.db.models import F
from store.models import Location
from .forms import LocationSearchForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import pytz
from datetime import datetime
from core.models import (
    User,
)


@csrf_exempt
def login_view(request):
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
            response["Location"] = "/dashboard/"  # Redirect to profile page
            response.status_code = 302
            return response
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    return render(request, "core/login.html")


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


def fetch_all_products():
    url = "http://127.0.0.1:8000/store/products/"
    products = []
    page = 1

    while True:
        response = requests.get(url, params={"page": page})
        if response.status_code != 200:
            break

        data = response.json()
        products.extend(data["results"])

        if not data["next"]:
            break

        page += 1

    return {"results": products, "count": len(products)}


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "core/product-detail.html"

    def product_detail_view(request, primary_key):
        try:
            product = Product.objects.get(pk=primary_key)
        except Product.DoesNotExist:
            raise Http404("Product not in warehouses/store rooms")

        return render(request, "core/product-detail.html", context={"product": product})


def haploid(request):
    return render(request, "core/haploid.html")


def dashboard(request):
    user = request.user

    query = request.GET.get("q")
    sort = request.GET.get("sort", "title")  # Default sort by title

    if query:
        products = Product.objects.filter(title__icontains=query).order_by(sort)
    else:
        products = Product.objects.all().order_by(sort)

    paginator = Paginator(products, 10)  # Show 10 products per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
        "product_list": page_obj,
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "next": page_obj.has_next(),
        "previous": page_obj.has_previous(),
        "query": query,
        "sort": sort,
    }
    return render(request, "core/dashboard.html", context)


def product_list(request):
    query = request.GET.get("q")
    sort = request.GET.get("sort", "title")  # Default sort by title

    if query:
        products = Product.objects.filter(title__icontains=query).order_by(sort)
    else:
        products = Product.objects.all().order_by(sort)

    paginator = Paginator(products, 10)  # Show 10 products per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "product_list": page_obj,
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "next": page_obj.has_next(),
        "previous": page_obj.has_previous(),
        "query": query,
        "sort": sort,
    }
    return render(request, "core/product-list.html", context)


def fetch_products(page=1):
    url = "http://127.0.0.1:8000/store/products/"
    response = requests.get(url, params={"page": page})
    if response.status_code == 200:
        return response.json()
    return None


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

    # Render the template with the products and user context
    return render(request, "core/product_list.html", {"products": page_obj}, context)


def index(request):
    return render(request, "core/index.html")


class RestockProducts(ListView):
    model = Product
    template_name = "core/restock-products.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(inventory__lt=F("restock_value"))


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
    if request.method == "POST":
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if action == 'delete':
            # and request.user.is_superuser:
            User.objects.filter(id__in=user_ids).delete()
            return redirect('view-users')
        else:
            return HttpResponseForbidden("You are not authorized to perform this action.")
    
    filter_by_staff = request.GET.get('filter_by_staff')
    if filter_by_staff == 'staff':
        users = User.objects.filter(is_staff=True)
    elif filter_by_staff == 'regular':
        users = User.objects.filter(is_staff=False)
    else:
        users = User.objects.all()

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
    return render(request, "core/view-users.html", {"users": users})


def transactions_view(request):
    return render(request, "core/transactions.html")


def notifications_view(request):
    return render(request, "core/notifications.html")


def users_crud_view(request):
    return render(request, "core/users.html")

def add_user(request):
    return render (request, "core/admin/add-user.html")

def add_product(request):
    return render (request, "core/admin/add-product.html")