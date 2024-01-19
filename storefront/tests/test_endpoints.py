from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from model_bakery import baker
from storefront.models import Collection
import pytest


@pytest.fixture
def post_collection(api_client):
    def create_collection(collection):
        return api_client.post("/storefront/collections/", collection)

    return create_collection


@pytest.fixture
def create_user(api_client):
    def authenticate(is_staff):
        return api_client.force_authenticate(user=User(is_staff=is_staff))

    return authenticate


@pytest.mark.django_db
class TestCollectionEndpoints:
    def test_if_users_get_collections_returns_200(self, api_client):
        endpoints = "/storefront/collections/"
        res = api_client.get(endpoints)

        assert res.status_code == status.HTTP_200_OK

    def test_if_users_get_collection_returns_200(self, api_client):
        collection = baker.make(Collection)
        res = api_client.get(f"/storefront/collections/{collection.id}", follow=True)

        assert res.status_code == status.HTTP_200_OK
        res = res.json()
        assert res["id"] == collection.id

    def test_if_users_anonymous_returns_401(self, post_collection):
        res = post_collection({"title": "a"})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_users_not_admin_returns_403(self, post_collection, create_user):
        create_user(False)
        res = post_collection({"title": "a"})

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_users_is_admin_returns_201(self, post_collection, create_user):
        create_user(True)
        res = post_collection({"title": "a"})

        assert res.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, post_collection, create_user):
        create_user(True)
        res = post_collection({"title": ""})

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.data["title"] is not None
    
    def test_if_anonymous_update_return_401(self, api_client):
        collection = baker.make(Collection)
        update_payload = {'title': 'Updated Title'}
        res = api_client.patch(f"/storefront/collections/{collection.id}/",data=update_payload)
        
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    