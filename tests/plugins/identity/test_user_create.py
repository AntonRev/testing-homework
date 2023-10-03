from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db()
def test_create_user(client: Client, user_data_factory: 'UserDataFactory', ):
    post_data = user_data_factory()
    response = client.post(
        reverse('identity:registration'),
        data=post_data
    )

    assert response.status_code == HTTPStatus.OK

