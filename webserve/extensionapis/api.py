import logging
import uuid
from datetime import datetime
from typing import List
from urllib.parse import urlparse

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander
from django.shortcuts import get_object_or_404
from ninja import Body, Router, pagination
from parser_utils.webutils.freeassociate_parser_driver import WebParserDriver
from users.apiauth import ApiKey

from .context_builder import build_page_domain_history, build_quiz_context
from .models import RawDocCapture, SingleUrl, SingleUrlFact
from .schemas import (
    DomSchema,
    RawDocCaptureSchema,
    RawDocCaptureWithContentSchema,
    WriteDomReturnSchemaWithHistory,
)


logger = logging.getLogger("default")

router = Router(auth=[ApiKey()], tags=["pages"])


@router.post("/writehtml", response=WriteDomReturnSchemaWithHistory)
def write_dom(request, data: DomSchema = Body(...)):
    user = request.auth
    url = data.url.href[:2048]

    logging.info("Receive request for %s: %s", user.pk, url)
    # Save a Raw File Save and upload.
    # Assume on server side we need to save (maybe relax later)

    container, filename, reader_container, reader_filename = upload_dom(user, data)
    context = None

    # create a SingleURL and return that id.
    obj, created = SingleUrl.objects.get_or_create(user=user, url=url)
    if created:
        obj.host = urlparse(url).netloc
        obj.save()
    else:
        # if this was created, we need to create an augmentation dict of previous quizzes, ect.
        context = build_quiz_context(obj)

    # Save any classification info to back end
    for k, v in data.domClassification.dict().items():
        if v is None:
            continue

        o, created = SingleUrlFact.objects.get_or_create(
            base_url=obj, fact_key=f"client_{k}", defaults={"fact_value": v}
        )
        if not created and o.fact_value != v:
            o.fact_value = v
            o.save()

    page_history_context = build_page_domain_history(obj)

    record = RawDocCapture.objects.create(
        guid=data.guid,
        capture_index=data.capture_index,
        user=user,
        location_container=container,
        location_path=filename,
        reader_location_container=reader_container,
        reader_location_path=reader_filename,
        url=url,
        title=data.title[:1024],
        url_model=obj,
    )

    d = {
        "raw_doc": str(record.pk),
        "url_obj": obj.pk,
        "visit_history": page_history_context,
    }

    if context is not None and context.quiz_obj is not None:
        d["quiz_context"] = {
            "previous_quiz": context.quiz_obj,
            "latest_results": context.quiz_last_result,
        }

    return d


def upload_new_version(request):
    """
    push the new files.
    save a new copy.
    if it succeeds, schedule a delete of old files
    """


@router.get("/rawdoccaptures/", response=List[RawDocCaptureSchema])
@pagination.paginate()
def get_raw_doc_list(request):
    return RawDocCapture.objects.filter(user=request.auth, active=1)


@router.get("/rawdoccaptures/{item_id}", response=RawDocCaptureWithContentSchema)
def get_raw_doc(request, item_id: str):
    raw_doc_capture = get_object_or_404(
        RawDocCapture, guid=item_id, active=1, user=request.auth
    )

    content = raw_doc_capture.get_content()
    doc_content = raw_doc_capture.get_content(True)
    if doc_content is None:
        doc_content = ""

    return RawDocCaptureWithContentSchema(
        user=str(request.auth.pk),
        url=raw_doc_capture.url,
        title=raw_doc_capture.title,
        content=content,
        capture_index=raw_doc_capture.capture_index,
        reader_content=doc_content,
    )


@router.post("/rawdoccaptures/{item_id}/parse")
def parse_raw_doc(request, item_id: int):
    raw_doc_capture = get_object_or_404(
        RawDocCapture, guid=item_id, active=1, user=request.auth
    )
    driver = WebParserDriver()
    driver.process_impression(raw_doc_capture)
    return {"message": "ok"}


def upload_dom(user, data: DomSchema):
    handler = RawDocCaptureHander()
    timestamp = datetime.today().strftime("%Y/%m/%d")
    filename_base = str(uuid.uuid4())
    container, filename = handler.upload(user, data.dom, timestamp, filename_base)
    if data.readerContent:
        reader_container, reader_filename = handler.upload(
            user, data.readerContent, timestamp, f"{filename_base}_reader"
        )
        return container, filename, reader_container, reader_filename
    return container, filename, "", ""
