from ninja import ModelSchema, Schema

from .models import RawDocCapture, SingleUrl

from quizzes.schemas import QuizContextSchema

from typing import Literal, List, Optional


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
    byline : str = ""  # this is capture by Mozilla reader mode
    readerContent : str = ""  # this is captured by Mozilla reader mode.
    siteName : str = ""  # this is captured by Mozilla reader mode.
    publishedTime : str = ""  # this is captured by Mozilla reader mode.
    domClassification : DomClassificationSchema


class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class SingleUrlHistorySchema(ModelSchema):

    recent_title : str

    class Meta:
        model = SingleUrl
        fields = ['id', 'date_added', 'url', 'host']


class RawDocCaptureHistorySchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = ['guid', 'date_added']


class RawDocCaptureWithContentSchema(Schema):

    user : str
    url : str
    title : str
    content : str


class RecentPageVisits(Schema):
    number_visits: int
    latest_visit: Optional[RawDocCaptureHistorySchema] = None


class VisitHistorySchema(Schema):
    recent_page_visits: RecentPageVisits
    recent_domain_visits: List[SingleUrlHistorySchema]


class WriteDomReturnSchema(Schema):

    raw_doc : str
    url_obj : int
    quiz_context : QuizContextSchema = None


class WriteDomReturnSchemaWithHistory(Schema):

    raw_doc : str
    url_obj : int
    quiz_context : QuizContextSchema = None
    visit_history : VisitHistorySchema
