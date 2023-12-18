from ninja import ModelSchema, Schema

from .models import RawDocCapture

class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class RawDocCaptureWithContentSchema(Schema):

    user : str
    url : str
    title : str
    content : str
