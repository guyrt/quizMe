import logging
from django.contrib.auth import authenticate

from ninja import Form, Router
from ninja.errors import AuthenticationError

from .models import AuthToken

from .apiauth import ApiKey, BurnOnRead, create_new_token
from .schemas import AuthTokenSchema, AuthTokenNonSecretSchema

from typing import List

logger = logging.getLogger("default")


router = Router(auth=[ApiKey()], tags=['users'])


@router.post("/tokens/create", auth=None, response=AuthTokenSchema)  # < overriding global auth
def create_token(request, username: str = Form(...), password: str = Form(...)):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token = create_new_token(user, "key")
        return AuthTokenSchema(
            user=user.email,
            key=token.key
        )
    raise AuthenticationError()


@router.post("/tokens/", response=List[AuthTokenNonSecretSchema])
def get_all_tokens(request):
    return AuthToken.objects.filter(user=request.auth)


@router.delete("/tokens/delete", auth=BurnOnRead())
def delete_token(request):
    return {}
