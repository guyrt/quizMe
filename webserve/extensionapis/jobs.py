from django_rq import job

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander


@job
def clean_raw_doc_capture(location_container: str, location_path: str):
    """Clean up an old file"""
    if location_container != "" and location_path != "":
        RawDocCaptureHander(location_container).delete(location_path)
