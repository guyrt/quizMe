import logging
import uuid
from datetime import datetime
from json import loads
from typing import List

from django.shortcuts import get_object_or_404

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander
from ninja import Router, pagination

from .auth import ApiKey
from .models import RawDocCapture
from .schemas import RawDocCaptureSchema, RawDocCaptureWithContentSchema

from parser_utils.webutils.freeassociate_parser_driver import WebParserDriver

logger = logging.getLogger("webstack")

router = Router(auth=ApiKey())


@router.post("/writehtml")
def write_dom(request):
    body = loads(request.body)
    user = request.auth
    logging.debug("Receive request for %s", user.pk)
    # Save a Raw File Save and upload.
    # Assume on server side we need to save (maybe relax later)
    handler = RawDocCaptureHander()
    container, filename = handler.upload(user, body['dom'], datetime.today().strftime('%Y/%m/%d'), str(uuid.uuid4()))

    # fire a task to parse
    RawDocCapture.objects.create(
        user=user,
        location_container=container,
        location_path=filename,
        url=body['url']['href'][:2048],
        title=body.get('title', '')[:1024],
    )

    return {'message': 'ok'}


@router.get("/rawdoccaptures/", response=List[RawDocCaptureSchema])
@pagination.paginate()
def get_raw_doc_list(request):
    return RawDocCapture.objects.filter(user=request.auth, active=1)


@router.get("/rawdoccaptures/{item_id}", response=RawDocCaptureWithContentSchema)
def get_raw_doc(request, item_id : int):
    raw_doc_capture = get_object_or_404(RawDocCapture, id=item_id, active=1, user=request.auth)

    content = raw_doc_capture.get_content()

    return RawDocCaptureWithContentSchema(
        user=str(request.auth.pk),
        url=raw_doc_capture.url,
        title=raw_doc_capture.title,
        content=content
    )


@router.post("/rawdoccaptures/{item_id}/parse")
def parse_raw_doc(request, item_id : int):
    raw_doc_capture = get_object_or_404(RawDocCapture, id=item_id, active=1, user=request.auth)
    driver = WebParserDriver()
    driver.process_impression(raw_doc_capture)
    return {'message': 'ok'}
