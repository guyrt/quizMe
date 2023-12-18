from ninja import ModelSchema, Schema

from .models import RawDocCapture, AuthTokens

class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class RawDocCaptureWithContentSchema(Schema):

    user : str
    url : str
    title : str
    content : str
    

class AuthTokenSchema(Schema):
    user : str
    key : str
