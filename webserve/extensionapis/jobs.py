from django_rq import job
from django_rq import enqueue

from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander
from mltrack.consumer_prompt_models import UserLevelDocVectorIndex, UserLevelVectorIndex
from .models import SingleUrl

import logging

logger = logging.getLogger("default")


@job
def handle_new_domain_remove(domain_to_remove: str):
    logger.info("Deleting domain %s", domain_to_remove)

    host_parts = domain_to_remove.split(".")
    url_objs = SingleUrl.objects.filter(
        host__endswith=domain_to_remove
    ).prefetch_related("rawdoccapture_set")
    for url in url_objs:
        logger.info("Deleting url %s for %s", url.pk, url.user_id)
        url_host_parts = url.host.split(".")
        if url_host_parts[-len(host_parts) :] == host_parts:
            for rdc in url.rawdoccapture_set.all():
                enqueue(
                    clean_raw_doc_capture, rdc.location_container, rdc.location_path
                )
                enqueue(
                    clean_raw_doc_capture,
                    rdc.reader_location_container,
                    rdc.reader_location_path,
                )

            num_vectors_deleted = UserLevelDocVectorIndex.objects.filter(
                user=url.user, doc_id=url.pk
            ).delete()
            num_vectors_deleted += UserLevelVectorIndex.objects.filter(
                user=url.user, doc_id=url.pk
            ).delete()
            logger.info(
                "delete %s total vectors on url %s", num_vectors_deleted, url.pk
            )
            url.delete()


@job
def clean_raw_doc_capture(location_container: str, location_path: str):
    """Clean up an old file"""
    if location_container != "" and location_path != "":
        RawDocCaptureHander(location_container).delete(location_path)
