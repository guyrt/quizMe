import logging
from django.contrib.auth import authenticate

from ninja import Form, Router
from ninja.errors import AuthenticationError, HttpError

from users.default_settings import populate_default_settings

from .models import AuthToken, LooseUserSettings, User

from .apiauth import ApiKey, create_new_token
from .schemas import AuthTokenSchema, AuthTokenNonSecretSchema, LooseUserSettingSchema

from typing import List
from datetime import datetime

logger = logging.getLogger("default")


router = Router(auth=[ApiKey()], tags=["users"])


@router.post(
    "/tokens/create", auth=None, response=AuthTokenSchema
)  # < overriding global auth
def create_token(request, username: str = Form(...), password: str = Form(...)):
    user = authenticate(request, email=username, password=password)
    if user is not None:
        token = create_new_token(user, "key")
        return AuthTokenSchema(user=user.email, key=token.key)
    raise AuthenticationError()


@router.post("/create", auth=None, response=AuthTokenSchema)
def create_user(request, email: str = Form(...), password: str = Form(...)):
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
    return AuthTokenSchema(user=user.email, key=token.key)


@router.post("/tokens/", response=List[AuthTokenNonSecretSchema])
def get_all_tokens(request):
    return AuthToken.objects.filter(user=request.auth)


# @router.delete("/tokens/delete", auth=BurnOnRead())
# def delete_token(request):
#     return {}


@router.post("/settings/resettodefault", response=List[LooseUserSettingSchema])
def reset_settings(request):
    populate_default_settings(request.auth)
    return LooseUserSettings.objects.filter(user=request.auth)


@router.get("/settings^", response=List[LooseUserSettingSchema])
def get_keys(request):
    return LooseUserSettings.objects.filter(user=request.auth)


@router.get("/settings/{key}", response=List[LooseUserSettingSchema])
def get_settings_by_key(request, key: str):
    user = request.auth
    return LooseUserSettings.objects.filter(user=user, key=key)


@router.post("/settings^", response=LooseUserSettingSchema)
def post_setting(request, payload: LooseUserSettingSchema):
    return LooseUserSettings.objects.create(
        user=request.auth, key=payload.key, value=payload.value
    )


@router.delete("/settings/{key}")
def delete_user_setting(request, key: str, value: str = None):
    # Assuming LooseUserSettings is a Django model associated with a user setting
    # and 'user' is a field in LooseUserSettings model representing the user
    query = LooseUserSettings.objects.filter(user=request.auth, key=key)
    if value is not None:
        query = query.filter(value=value)
    num_settings_deleted = query.delete()
    payload = {"num_settings_deleted": num_settings_deleted, "num_objects_deleted": 0}

    # handle specific key types.
    if key == LooseUserSettings.KnownKeys.DomainExclude:
        # todo
        payload["num_objects_deleted"] = 1

    return payload
