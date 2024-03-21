import pytest
from users.models import AuthToken, User
from mixer.backend.django import mixer

from ninja.testing import TestClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def existing_user():
    """
    Dummy example. Mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    user = mixer.blend(User, email="exists@user.com")
    mixer.blend(AuthToken, user=user, key="test_123", name="testtoken")
    yield user


class TestClientWithDefaultHeaders(TestClient):
    def __init__(self, api, default_headers=None):
        super().__init__(api)
        self.default_headers = default_headers or {
            "X-API-KEY": "test_123",
            "Content-Type": "application/json",
        }

    def request(self, method, path, data, **kwargs):
        headers = kwargs.pop("headers", {})
        # Update the headers with default headers, giving priority to any headers explicitly passed to the request
        headers = {**self.default_headers, **headers}
        return super().request(method, path, data, headers=headers, **kwargs)
