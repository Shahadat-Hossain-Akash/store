from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post("/storefront/carts/")
        res = response.json()
        self.cart_id = res["id"]

    @task(2)
    def view_products(self):
        collection_id = randint(2, 6)
        self.client.get(
            f"/storefront/products/?collection_id={collection_id}",
            name="/storefront/products/",
        )

    @task(4)
    def view_product(self):
        product_id = randint(1, 100)
        self.client.get(
            f"/storefront/products/{product_id}/",
            name="/storefront/products/:id",
        )

    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 100)
        self.client.post(
            f"/storefront/carts/{self.cart_id}/cartitems/",
            name="/storefront/carts/cartitems/",
            json={"product_id": product_id, "quantity": 1},
        )
