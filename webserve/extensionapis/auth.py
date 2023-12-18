from typing import Any
from django.http import HttpRequest
import secrets
from ninja.security import APIKeyHeader

from .models import AuthTokens
from users.models import User


class ApiKey(APIKeyHeader):
    param_name = 'X-API-Key'

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        try:
            return AuthTokens.objects.get(key=key).user
        except AuthTokens.DoesNotExist:
            pass


def create_token(user : User, name : str) -> AuthTokens:
    token_content = f"fa0_{secrets.token_urlsafe(35)}"
    return AuthTokens.objects.create(
        key=token_content,
        user=user,
        name=str
    )
