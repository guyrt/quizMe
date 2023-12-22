import logging
from django.contrib.auth import authenticate

from ninja import Form, Router
from ninja.errors import AuthenticationError, HttpError

from .models import AuthToken, User

from .apiauth import ApiKey, BurnOnRead, create_new_token
from .schemas import AuthTokenSchema, AuthTokenNonSecretSchema

from typing import List
from datetime import datetime

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


@router.post("/create", auth=None, response=AuthTokenSchema)
def create_user(request, email : str = Form(...), password: str = Form(...)):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # create the user - verified none exists.
        user = User.objects.create(email=email, password=password)
        logger.info("Creating account for %s", email)
    else:
        user2 = authenticate(request, username=email, password=password)
        if user2 == user and not user.is_active:
            # Then re-enable them!
            user.is_active = True
            user.save()
        else:
            logger.info("username already exists: %s", email)
            raise HttpError(409, "Already exists")

    # Fall through from except and one else path
    token = create_new_token(user, f"Created at {datetime.now()}")
    return AuthTokenSchema(
        user=user.email,
        key=token.key
    )


@router.post("/tokens/", response=List[AuthTokenNonSecretSchema])
def get_all_tokens(request):
    return AuthToken.objects.filter(user=request.auth)


@router.delete("/tokens/delete", auth=BurnOnRead())
def delete_token(request):
    return {}
