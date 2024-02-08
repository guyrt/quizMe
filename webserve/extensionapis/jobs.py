from django_rq import job

@job
def clean_raw_doc_capture(location_container : str, location_path : str):
    """Clean up an old file"""
    