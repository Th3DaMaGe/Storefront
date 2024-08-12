from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
import pytest


class TestCreateCart:
    def test_if_anonymous_user_returns_401(self, api_client):
        """Test if an anonymous user receives 401 status code. Unauthorised access is prohibited -> Cannot make a cart when unauthorised i.e. not admin nor customer"""
        response = api_client.post("/store/carts/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_if_admin_user_can_create_cart(self, api_client):
        """Test if admin can create a cart"""
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post("/store/carts/", {"created_at": 1998 - 12 - 22})

        assert response.status_code == status.HTTP_201_CREATED
