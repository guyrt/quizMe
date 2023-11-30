from ninja import Router
from json import loads
import uuid
from datetime import datetime

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander

from .auth import ApiKey

from .models import RawDocCapture

import logging
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
        location_path=filename
    )

    return {'message': 'ok'}
