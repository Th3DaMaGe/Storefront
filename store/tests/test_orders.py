from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker
from store.models import Order


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
    def test_if_order_data_is_valid_returns_201(self, api_client, authenticate):
        """Test if valid order data has been provided."""
        authenticate(is_staff=True)
        order = baker.make(Order)

        response = api_client.post(f"/store/products/{order.id}/")

        print(order.__dict__)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveOrder:
    def test_if_order_exists_returns_200(self, authenticate, api_client):
        authenticate(is_staff=True)

        order = baker.make(Order)
        response = api_client.get(f"/store/orders/{order.id}/")

        print(order.__dict__)

        assert response.status_code == status.HTTP_200_OK
        # assert response.data == {
        #     "id": order.id,
        #     "placed_at": order.placed_at,
        #     "payment_status": order.payment_status,
        #     "customer": order.customer.id,
        #     # "items": [1]  # No items in this test as we are not adding any items to the order.
        # }
