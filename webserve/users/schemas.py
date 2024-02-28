from ninja import ModelSchema, Schema

from .models import AuthToken, LooseUserSettings
    

class AuthTokenSchema(Schema):
    user : str
    key : str


class AuthTokenNonSecretSchema(ModelSchema):
    class Meta:
        model = AuthToken
        fields = ['id', 'user', 'name']


class LooseUserSettingSchema(ModelSchema):
    class Meta:
        model = LooseUserSettings
        fields = ['key', 'value']