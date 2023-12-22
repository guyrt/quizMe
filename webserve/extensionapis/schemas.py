from ninja import ModelSchema, Schema

from .models import RawDocCapture

from typing import Literal


class DomClassificationSchema(Schema):

    classification : Literal["article", "unknown"]

    reason : Literal["hasArticleTag", "dashCount", "textContent", "id", "class", "fallthrough"]

    idLookup : str | None

    classLookup : str | None


class DomSchema(Schema):

    dom : str  # HTML representation of the page contents.
    url : dict  # Location object.
    title : str = ""
    recordtime : int  # integer timestamp

    domClassification : DomClassificationSchema



class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class RawDocCaptureWithContentSchema(Schema):

    user : str
    url : str
    title : str
    content : str
