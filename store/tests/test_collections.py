from django.contrib.auth.models import User
from rest_framework import status
import pytest
from store.models import Collection, Product
from model_bakery import baker

"""This function reduces boilerplate code namely:
response = api_client.post("/store/collections/", {"title": "A"})"""


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)

    return do_create_collection
    # AAA (arrange, Act Assert)


"""This class has the tests related to creating a collection."""


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client, create_collection):
        response = create_collection({"title": "title"})
        # response = api_client.post("/store/collections/", {"title": "A"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(
        self, api_client, authenticate, create_collection
    ):
        #  Notice the authenticate method rplaces this code -> api_client.force_authenticate(user=User(is_staff=True))
        authenticate(is_staff=False)

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, api_client):
        authenticate(is_staff=True)

        response = api_client.post("/store/collections/", {"title": "A"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


"""This class is tests the retrieval of collections in various test conditions, invalid data; anon users, valid data etc..."""


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        # Note that all our tests should be independent of each other. Create collection first then retrieve it
        # Note that we have to actually implement the collection creation method in order to test, this violates policy but 🤷🏾‍♂️
        # Arrange
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        print(collection.__dict__)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"id": collection.id, "title": collection.title, "products_count": 0}
    