import datetime as dt
from typing import Protocol, final, TypedDict
from typing import TypeAlias, Callable

import pytest
from mimesis.locales import Locale
from mimesis.schema import Field, Schema
from typing_extensions import Unpack

from server.apps.identity.models import User


@final
class UserData(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    email: str
    first_name: str
    last_name: str
    date_of_birth: dt.datetime
    address: str
    job_title: str
    phone: str
    lead_id: bool
    is_staff: bool
    is_active: bool


@final
class UserDataFactory(Protocol):
    def __call__(self, **fields: Unpack[UserData], ) -> UserData:
        """User data factory protocol."""


@pytest.fixture()
def user_data_factory() -> UserDataFactory:
    """Returns factory for fake random data for regitration."""

    def factory(**fields: Unpack[UserData]) -> UserData:
        mf = Field(locale=Locale.RU)
        schema = Schema(schema=lambda: {
            'email': mf('person.email'),
            'first_name': mf('person.first_name'),
            'last_name': mf('person.last_name'),
            'date_of_birth': mf('datetime.date'),
            'address': mf('address.city'),
            'job_title': mf('person.occupation'),
            'phone': mf('person.telephone'),
            # 'lead_id': mf('increment'),
            # 'is_staff': False,
            # 'is_active': True,
        }, iterations=1)
        return {**schema.create()[0],  # type: ignore[misc]
                **fields}

    return factory


UserAssertion: TypeAlias = Callable[[str, UserData], None]


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    def factory(email: str, expected: UserData) -> None:
        user = User.objects.get(email=email)

        assert user.id
        assert user.is_active
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            assert getattr(user, field_name) == data_value

    return factory


@pytest.fixture()
def user_data(registration_data: 'RegistrationData') -> 'UserData':
    """
    We need to simplify registration data to drop passwords.
    Basically, it is the same as ``registration_data``, but without passwords.
    """
    return {  # type: ignore[return-value]
        key_name: value_part
        for key_name, value_part in registration_data.items()
        if not key_name.startswith('password')
    }
