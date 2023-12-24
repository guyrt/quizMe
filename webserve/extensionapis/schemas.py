from ninja import ModelSchema, Schema

from .models import RawDocCapture

from quizzes.schemas import SimpleQuizSchema

from typing import Literal, List


class DomClassificationSchema(Schema):

    classification : Literal["article", "unknown"]

    reason : Literal["hasArticleTag", "dashCount", "textContent", "id", "class", "fallthrough"]

    idLookup : str = None

    classLookup : str = None


class DomLocation(Schema):
    """Subset of browser Location object."""
    href : str


class DomSchema(Schema):

    dom : str  # HTML representation of the page contents.
    url : DomLocation 
    title : str = ""
    recordTime : int  # integer timestamp

    domClassification : DomClassificationSchema


class UrlContextSchema(Schema):

    previous_quiz : SimpleQuizSchema
    latest_results : List[int]


class WriteDomReturnSchema(Schema):

    raw_doc : int
    url_obj : int
    url_context : UrlContextSchema = None


class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class RawDocCaptureWithContentSchema(Schema):

    user : str
    url : str
    title : str
    content : str
