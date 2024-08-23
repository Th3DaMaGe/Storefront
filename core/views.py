from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


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
            response["Location"] = "/profile/"  # Redirect to profile page
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
    return render(request, "core/profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")
