from typing import Any
from django.http import HttpRequest
import secrets
from ninja.security import APIKeyHeader

from users.models import AuthToken, User


class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        try:
            return AuthToken.objects.get(key=key).user
        except AuthToken.DoesNotExist:
            pass


class BurnOnRead(APIKeyHeader):
    """Special api key header that will delete the auth key if it exists. Use on DELETE"""

    param_name = "X-API-Key"

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        try:
            a = AuthToken.objects.get(key=key)
            u = a.user
            a.delete()
            return u
        except AuthToken.DoesNotExist:
            pass


def create_new_token(user: User, name: str) -> AuthToken:
    token_content = f"fa0_{secrets.token_urlsafe(35)}"
    return AuthToken.objects.create(key=token_content, user=user, name="name")
