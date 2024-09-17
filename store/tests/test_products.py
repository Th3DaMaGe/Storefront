from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker
from store.models import Product


class TestCreateProduct:
    def test_if_user_anonymous_returns_401(self):
        """Test if an anonymous user receives 401 status code. Unauthorised access is prohibited."""
        client = APIClient()
        response = client.post(
            "/store/products/",
            {
                "title": "A",
                "description": "test description",
                "inventory": 10,
                "unit_price": 10,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self):
        # Only admins can create products
        client = APIClient()
        client.force_authenticate(user={})
        response = client.post(
            "/store/products/",
            {
                "title": "A",
                "description": "test description",
                "inventory": 10,
                "unit_price": 10,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post(
            "/store/products/",
            {
                "title": "",
                "description": "test description",
                "inventory": 10,
                "unit_price": 10,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    @pytest.mark.django_db
    def test_if_product_data_is_valid_returns_201(self, api_client, authenticate):
        authenticate(is_staff=True)
        response = api_client.post(
            "/store/products/",
            {
                "title": "Al",
                "description": "test description",
                "inventory": 10,
                "unit_price": 10.00,
                "collection": "test collection",
                "last_update": "2013-10-18 00:00:00",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveProduct:
    """
    Test to ensure that a GET request to the product detail endpoint returns a 200 status code
    when the product exists.

    Args:
        self: The instance of the test case.
        api_client: The API client used to make requests.

    Steps:
        1. Create a product instance using the baker library.
        2. Make a GET request to the product detail endpoint using the product's ID.
        3. Assert that the response status code is 200 OK.
        # 4. Optionally, assert that the response data matches the product's attributes.
    """

    def test_if_product_exists_returns_200(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_200_OK
        # assert response.data == { 'id': product.id, "title": product.title, "description": product.description, "slug": product.slug, "inventory": product.inventory, "last_update": product.last_update, "unit_price" : product.unit_price, "collection":product.collection, "images": product.images, "price_with_tax": 0 }
