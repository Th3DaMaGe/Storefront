from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    # host = "http://your-base-url.com"  # Replace with your actual base URL

    def on_start(self):
        # Fetch the CSRF token
        response = self.client.get("/store/carts/")
        csrftoken = response.cookies["csrftoken"]

        # Create a new cart
        response = self.client.post(
            "/store/carts/",
            headers={"X-CSRFToken": csrftoken},
            cookies={"csrftoken": csrftoken},
        )
        result = response.json()
        self.cart_id = result["id"]

    @task(2)
    def view_products(self):
        collection_id = randint(2, 6)
        self.client.get(
            f"/store/products/?collection_id={collection_id}", name="/store/products"
        )

    @task(4)
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(f"/store/products/{product_id}", name="/store/products/:id")

    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 10)
        # csrftoken = self.client.cookies["csrftoken"]
        self.client.post(
            f"/store/carts/{self.cart_id}/items/",
            name="/store/carts/items",
            json={"product_id": product_id, "quantity": 1},
            # headers={"X-CSRFToken": csrftoken},
            # cookies={"csrftoken": csrftoken},
        )
