import logging
import uuid
from datetime import datetime
from typing import List
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django_rq import enqueue

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander
from django.shortcuts import get_object_or_404
from ninja import Body, Router, pagination
from parser_utils.webutils.freeassociate_parser_driver import process_raw_doc
from users.apiauth import ApiKey
from mltrack.search.relevant_chunks import NoChunksError, find_relevant_chunks

from .context_builder import build_page_domain_history, build_quiz_context
from .models import RawDocCapture, SingleUrl, SingleUrlFact
from .jobs import clean_raw_doc_capture
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

    # this is assumed atomic due to uniqueness constraint on user/url
    obj, created = SingleUrl.objects.get_or_create(
        user=user, url=url, defaults={"host": urlparse(url).netloc}
    )
    if not created:
        # if this was not created, we need to create an augmentation dict of previous quizzes, ect.
        context = build_quiz_context(obj)

    _save_history(data, obj)

    page_history_context = build_page_domain_history(obj)

    try:
        r, created = RawDocCapture.objects.get_or_create(
            id=data.guid,
            defaults={
                "capture_index": data.capture_index,
                "user": user,
                "location_container": container,
                "location_path": filename,
                "reader_location_container": reader_container,
                "reader_location_path": reader_filename,
                "url": url,
                "title": data.title[:1024],
                "url_model": obj,
            },
        )
        if not created:
            enqueue(clean_raw_doc_capture, container, filename)
            enqueue(clean_raw_doc_capture, reader_container, reader_filename)
            # no need to try to save... this has lower capture index.
        else:
            enqueue(process_raw_doc, obj.pk)
    except ValidationError:
        pass  # this happens if a different upload beat us to it.

    d = {
        "raw_doc": str(data.guid),
        "url_obj": str(obj.pk),
        "visit_history": page_history_context,
    }

    if context is not None and context.quiz_obj is not None:
        d["quiz_context"] = {
            "previous_quiz": context.quiz_obj,
            "latest_results": context.quiz_last_result,
        }

    return d


@router.post("/rewritehtml")
def upload_new_version(request, data: DomSchema = Body(...)):
    """
    push the new files.
    save a new copy.
    if it succeeds, schedule a delete of old files.
    """
    logger.info("Got more recent upload for %s", data.guid)
    user = request.auth
    url = data.url.href[:2048]

    # do uploads (copy out)
    container, filename, reader_container, reader_filename = upload_dom(user, data)

    # this is assumed atomic due to uniqueness constraint on user/url
    url_obj, _ = SingleUrl.objects.get_or_create(
        user=user, url=url, defaults={"host": urlparse(url).netloc}
    )

    saved_new_files = False
    try:
        raw_doc_capture, created = RawDocCapture.objects.get_or_create(
            id=data.guid,
            defaults={
                "capture_index": data.capture_index,
                "user": user,
                "location_container": container,
                "location_path": filename,
                "reader_location_container": reader_container,
                "reader_location_path": reader_filename,
                "url": url,
                "title": data.title[:1024],
                "url_model": url_obj,
            },
        )

        if not created:
            logger.info(
                "Reupload for %s used existing record. Updating index from %s to %s",
                raw_doc_capture.pk,
                raw_doc_capture.capture_index,
                data.capture_index,
            )
            # todo - populate object and trigger cleanup of old items.
            if raw_doc_capture.capture_index < data.capture_index:
                enqueue(
                    clean_raw_doc_capture,
                    raw_doc_capture.location_container,
                    raw_doc_capture.location_path,
                )
                enqueue(
                    clean_raw_doc_capture,
                    raw_doc_capture.reader_location_container,
                    raw_doc_capture.reader_location_path,
                )

                raw_doc_capture.capture_index = data.capture_index
                raw_doc_capture.user = raw_doc_capture.user
                raw_doc_capture.location_container = container
                raw_doc_capture.location_path = filename
                raw_doc_capture.reader_location_container = reader_container
                raw_doc_capture.reader_location_path = reader_filename
                raw_doc_capture.url = url
                raw_doc_capture.title = data.title[:1024]
                raw_doc_capture.url_model = url_obj
                raw_doc_capture.save()
                saved_new_files = True

                enqueue(process_raw_doc, url_obj.pk)
            else:
                logger.info(
                    "out of sync timestamps: existing is %s and new is %s",
                    raw_doc_capture.capture_index,
                    data.capture_index,
                )
        else:
            logger.info("reupload created new record for %s", data.guid)
    except ValidationError:
        # This means we are not most recent.
        logger.warning(f"Tried to save out of order doc for {data.guid}")

    if saved_new_files:
        return {"message": "ok"}
    else:
        enqueue(clean_raw_doc_capture, container, filename)
        enqueue(clean_raw_doc_capture, reader_container, reader_filename)

        return {"message": "ooo"}


def _save_history(data: DomSchema, url_obj: SingleUrl):
    # Save any classification info to back end
    for k, v in data.domClassification.dict().items():
        if v is None:
            continue

        o, created = SingleUrlFact.objects.get_or_create(
            base_url=url_obj, fact_key=f"client_{k}", defaults={"fact_value": v}
        )
        if not created and o.fact_value != v:
            o.fact_value = v
            o.save()


@router.get("/rawdoccaptures/", response=List[RawDocCaptureSchema])
@pagination.paginate()
def get_raw_doc_list(request):
    return RawDocCapture.objects.filter(user=request.auth, active=1)


@router.get("/rawdoccaptures/{item_id}^", response=RawDocCaptureWithContentSchema)
def get_raw_doc(request, item_id: uuid.UUID):
    raw_doc_capture = get_object_or_404(
        RawDocCapture, id=item_id, active=1, user=request.auth
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


@router.get("/url/{item_id}/reprocess")
def reprocess_raw_doc(request, item_id: uuid.UUID):
    single_url = get_object_or_404(SingleUrl, id=item_id, active=1, user=request.auth)
    enqueue(process_raw_doc, single_url.pk)
    return {"status": "ok"}


@router.get("/rawdoccaptures/{item_id}/search")
def search_doc(request, item_id: uuid.UUID):
    raw_doc_capture = get_object_or_404(
        RawDocCapture, id=item_id, active=1, user=request.auth
    )
    try:
        return find_relevant_chunks(raw_doc_capture.url_model)
    except NoChunksError:
        return {"status": "wait"}


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
