from ninja import ModelSchema, Schema

from .models import RawDocCapture, SingleUrl

from quizzes.schemas import SimpleQuizSchema

from typing import Literal, List, Optional


class DomClassificationSchema(Schema):
    classification: Literal["article", "serp", "unknown"]

    reason: Literal[
        "hasArticleTag",
        "dashCount",
        "textContent",
        "serp",
        "id",
        "class",
        "fallthrough",
    ]

    idLookup: str = None

    classLookup: str = None


class DomLocation(Schema):
    """Subset of browser Location object."""

    href: str


class DomSchema(Schema):
    guid: str  # primary key suggested by the client
    capture_index: int  # should be 0 on first write.
    dom: str  # HTML representation of the page contents.
    url: DomLocation
    title: str = ""
    recordTime: int  # integer timestamp
    byline: str = ""  # this is capture by Mozilla reader mode
    readerContent: str = ""  # this is captured by Mozilla reader mode.
    siteName: str = ""  # this is captured by Mozilla reader mode.
    publishedTime: str = ""  # this is captured by Mozilla reader mode.
    domClassification: DomClassificationSchema


class RawDocCaptureSchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = "__all__"


class SingleUrlHistorySchema(ModelSchema):
    recent_title: str | None = None

    class Meta:
        model = SingleUrl
        fields = ["id", "date_added", "url", "host"]


class RawDocCaptureHistorySchema(ModelSchema):
    class Meta:
        model = RawDocCapture
        fields = ["id", "date_added"]


class RawDocCaptureWithContentSchema(Schema):
    user: str
    capture_index: int
    url: str
    title: str
    content: str
    reader_content: str


class RecentPageVisits(Schema):
    number_visits: int
    latest_visit: Optional[RawDocCaptureHistorySchema] = None


class VisitHistorySchema(Schema):
    recent_page_visits: RecentPageVisits
    recent_domain_visits: List[SingleUrlHistorySchema]


class WriteDomReturnSchema(Schema):
    raw_doc: str
    url_obj: str
    quiz_context: SimpleQuizSchema = None


class WriteDomReturnSchemaWithHistory(WriteDomReturnSchema):
    visit_history: VisitHistorySchema


class SearchDoc(Schema):
    doc_id: str
    doc_url: str
    score: float


class WaitResponse(Schema):
    status: str
