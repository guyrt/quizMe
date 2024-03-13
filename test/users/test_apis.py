from unittest.mock import MagicMock
from _pytest.monkeypatch import MonkeyPatch
import pytest
from ninja.testing import TestClient
from users.models import User
from users.api import router


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return TestClient(router)


@pytest.fixture
def populate_default_settings(monkeypatch: MonkeyPatch):
    mock_settings = MagicMock()

    monkeypatch.setattr("users.models.populate_default_settings", mock_settings)
    yield mock_settings


def test_create_user_success(api_client, populate_default_settings):
    email = "new@example.com"
    password = "password"
    response = api_client.post("/create", {"email": email, "password": password})
    assert response.status_code == 200
    assert "key" in response.json()
    assert User.objects.filter(email=email).exists()

    populate_default_settings.assert_called_once()
    new_user = User.objects.get()
    assert new_user.check_password("password")


def test_reactivate_user_success(api_client, populate_default_settings):
    # Create an inactive user first
    u = User.objects.create(email="inactive@example.com", is_active=False)
    populate_default_settings.reset_mock()
    u.set_password("password")
    u.save()

    response = api_client.post(
        "/create", {"email": "inactive@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert User.objects.get(email="inactive@example.com").is_active

    populate_default_settings.assert_not_called()


def test_create_user_already_exists(api_client, populate_default_settings):
    u = User.objects.create_user(email="exists@example.com")
    populate_default_settings.reset_mock()
    u.set_password("password")
    u.save()

    response = api_client.post(
        "/create", {"email": "exists@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "key" in response.json()

    populate_default_settings.assert_not_called()


def test_create_user_already_exists_bad_password(api_client, populate_default_settings):
    u = User.objects.create_user(email="exists@example.com")
    populate_default_settings.reset_mock()
    u.set_password("password")
    u.save()

    response = api_client.post(
        "/create", {"email": "exists@example.com", "password": "newpassword"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Already exists"}

    populate_default_settings.assert_not_called()
