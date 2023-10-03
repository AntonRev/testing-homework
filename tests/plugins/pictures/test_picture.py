from http import HTTPStatus
from typing import TypedDict, final, Unpack

import pytest

from mimesis import Field, Locale, Schema
from django.test import Client

from server.apps.identity.models import User
from server.apps.pictures.models import FavouritePicture


@final
class FavouritesDataForm(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    foreign_id: str
    url: str


@pytest.fixture()
def favourites_data_form() -> FavouritesDataForm:
    """Returns factory for fake random data."""

    def factory(**fields: Unpack[FavouritesDataForm]) -> FavouritesDataForm:
        mf = Field(locale=Locale.RU)
        schema = Schema(schema=lambda: {
            'foreign_id': mf('increment'),
            'url': mf('url'),
        }, iterations=1)
        return {**schema.create()[0],  # type: ignore[misc]
                **fields}

    return factory


@pytest.fixture()
def client_auth(client: Client):
    def factory() -> Client:
        User.objects.create_user(password="johnpassword", email="test@test.ru")
        client.login(email="test@test.ru", password="johnpassword")
        return client

    return factory


@pytest.mark.django_db()
def test_picture_form(client_auth: Client, favourites_data_form: 'FavouritesDataForm', ):
    post_data = favourites_data_form()
    registration_form = FavouritePicture(post_data)
    assert str(registration_form) == "<Picture {0} by {1}>".format(registration_form.foreign_id,
                                                                   registration_form.user_id)

    client = client_auth()
    response = client.post("/pictures/dashboard", data=post_data)

    assert response.get("location") == '/pictures/dashboard'
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
def test_get_picture_dashboard(client_auth: Client):
    client = client_auth()

    response = client.get("/pictures/dashboard")

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_get_picture_favourites(client_auth: Client):
    client = client_auth()

    response = client.get("/pictures/favourites")

    assert response.status_code == HTTPStatus.OK
