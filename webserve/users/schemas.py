from ninja import ModelSchema, Schema

from .models import AuthToken


class AuthTokenSchema(Schema):
    user: str
    key: str


class AuthTokenNonSecretSchema(ModelSchema):
    class Meta:
        model = AuthToken
        fields = ["id", "user", "name"]
