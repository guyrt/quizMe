import pypdf

from privateuploads.models import RawUpload, DocumentFile


class RFPDocumentExtract:

    def __init__(self) -> None:
        pass

    def parse(self, raw_doc_id : int):
        raw_obj = RawUpload.objects.get(id=raw_doc_id)

        # Step 1: extract the doc and save
        if raw_obj.format == 'pdf':
            self._extract_pdf(raw_obj)
        else:
            raise NotImplementedError(f"RawUpload {raw_obj.pk}: {raw_obj.format}")

        # Step 2: queue up GPT parse

    def _extract_pdf(self, raw_obj : RawUpload) -> DocumentFile:
        pass


def execute_rfp_parse(raw_doc_id : int):
    """This is our queued request."""
    RFPDocumentExtract().parse(raw_doc_id)
