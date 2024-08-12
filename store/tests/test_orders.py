from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
import pytest


class TestCreateOrders:
    def test_if_user_anonymous_returns_401(self):
        """Test if an anonymous user receives 401 status code. Unauthorised access is prohibited -> Cannot make orders when unauthorised i.e. not admin nor customer"""
        client = APIClient()
        response = client.post(
            "/store/orders/",
            {
                "placed_at": "2013-12-12 00:00:00",
                "payment_status": "p",
                "customer": 2,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_if_order_data_is_valid_returns_201(self):
        """Test if valid order data has been provided."""
        client = APIClient()
        client.force_authenticate(user={})
        response = client.post(
            "/store/orders/",
            {
                "placed_at": "2013-12-12 00:00:00",
                "payment_status": "p",
                "customer": 2,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
