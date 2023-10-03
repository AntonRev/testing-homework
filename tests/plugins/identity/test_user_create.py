import json
from http import HTTPStatus
from pprint import pprint

import pytest
from django.test import Client
from django.urls import reverse
import logging

from server.apps.identity.infrastructure.django.forms import RegistrationForm
from server.apps.identity.models import User

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@pytest.fixture()
def client_auth(client: Client, user_data_factory: 'UserDataFactory'):
    def factory() -> Client:
        user = user_data_factory()
        User.objects.create_user(password=user['password1'], email=user['email'])
        client.login(password=user['password1'], email=user['email'])
        return client, user

    return factory


def del_key_in_data(data: dict, key: str) -> 'UserData':
    """
    We need to simplify registration data to drop passwords.
    Basically, it is the same as ``registration_data``, but without passwords.
    """
    return {  # type: ignore[return-value]
        key_name: value_part
        for key_name, value_part in data.items()
        if not key_name.startswith(key)
    }


@pytest.mark.django_db()
def test_create_valid_user(client: Client, user_data_factory: 'UserDataFactory'):
    post_data = user_data_factory()

    registration_form = RegistrationForm(post_data)
    assert registration_form.is_valid() == True

    response = client.post("/identity/registration", data=registration_form.data)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
@pytest.mark.parametrize('field', ("email", 'first_name', 'last_name',
                                   'address', 'job_title', 'phone'))
def test_no_valid_user_form(client: Client, user_data_factory: 'UserDataFactory', field):
    post_data = del_key_in_data(user_data_factory(), field)

    registration_form = RegistrationForm(post_data)
    assert registration_form.is_valid() == False

    response = client.post("/identity/registration", data=registration_form.data)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_create_user_without_date_of_birth(client: Client, user_data_factory: 'UserDataFactory', ):
    post_data = user_data_factory(**{"date_of_birth": ""})

    registration_form = RegistrationForm(post_data)
    assert registration_form.is_valid() == True

    response = client.post("/identity/registration", data=registration_form.data)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
def test_update(user_data_factory: 'UserDataFactory', client_auth: Client):
    client, user_old = client_auth()
    user_new = user_data_factory()

    registration_form = RegistrationForm(user_new)
    assert registration_form.is_valid() == False  # TODO: добавить количество пользователей через "seed"

    response = client.put("/identity/registration", data=registration_form.data)
    assert response.status_code == HTTPStatus.FOUND
