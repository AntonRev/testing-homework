import json
from http import HTTPStatus
from pprint import pprint

import pytest
from django.test import Client
from django.urls import reverse
import logging

from server.apps.identity.infrastructure.django.forms import RegistrationForm

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
def test_create_valid_user(client: Client, user_data_factory: 'UserDataFactory', ):
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
