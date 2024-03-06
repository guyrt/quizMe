from django_rq import job
from django_rq import enqueue

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander
from .models import SingleUrl


@job
def handle_new_domain_remove(domain_to_remove : str):
    url_objs = SingleUrl.objects.filter(host__endswith=domain_to_remove).prefetch_related('rawdoccapture_set')
    for u in url_objs:
        for rdc in u.rawdoccapture_set.all():
            enqueue(clean_raw_doc_capture, rdc.location_container, rdc.location_path)
            enqueue(clean_raw_doc_capture, rdc.reader_location_container, rdc.reader_location_path)
    url_objs.delete()

@job
def clean_raw_doc_capture(location_container: str, location_path: str):
    """Clean up an old file"""
    if location_container != "" and location_path != "":
        RawDocCaptureHander(location_container).delete(location_path)
