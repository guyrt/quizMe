from typing import Any
from django.http import HttpRequest
from django.shortcuts import render
from ninja.security import APIKeyHeader

from .models import AuthTokens


class ApiKey(APIKeyHeader):
    param_name = 'X-API-Key'

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        try:
            return AuthTokens.objects.get(key=key).user
        except AuthTokens.DoesNotExist:
            pass


