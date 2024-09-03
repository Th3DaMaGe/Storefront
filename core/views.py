from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from store.models import Product
from django.views import generic
from django.http import Http404
import requests
from django.views.generic import ListView
from django.db.models import F


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
    page = request.GET.get("page", 1)
    products_data = fetch_products()

    if products_data:
        products = products_data["results"]
        total_products = products_data["count"]
        paginator = Paginator(products, 10)
        page_obj = paginator.get_page(page)
    else:
        products = []
        total_products = 0
        page_obj = None

    context = {
        "username": user.username,
        "is_staff": user.is_staff,
        "email": user.email,
        "page_obj": page_obj,
        "total_products": total_products,
        # "fullname": f"{user.fullname} {user.last_name}",
    }
    return render(request, "core/profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")


# def fetch_products():
#     url = "http://127.0.0.1:8000/store/products/"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     return None


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
    products = Product.objects.all()
    paginator = Paginator(products, 10)  # Show 10 products per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/product_list.html", {"products": page_obj})


def index(request):
    return render(request, "core/index.html")


class RestockProducts(ListView):
    model = Product
    template_name = "core/restock-products.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(inventory__lt=F("restock_value"))
