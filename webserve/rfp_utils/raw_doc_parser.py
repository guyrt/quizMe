import json
from django_rq import job

from azurewrapper.rfp.rawdocs_handler import RfpRawBlobHander
from azurewrapper.rfp.extractedtext_handler import RfpExtractedTextBlobHander
from privateuploads.models import DocumentFile, DocumentExtract
from rfp_utils.pdf_parser import PdfParser


class RFPDocumentExtract:

    def __init__(self) -> None:
        pass

    def parse(self, doc_id : int):
        raw_obj = DocumentFile.objects.get(id=doc_id)

        doc_files = []

        # Step 1: extract the doc and save
        if raw_obj.doc_format == 'pdf':
            doc_files.append(self._extract_pdf(raw_obj))
        else:
            raise NotImplementedError(f"RawUpload {raw_obj.pk}: {raw_obj.doc_format}")

        # Step 2: queue up GPT parse


    def _extract_pdf(self, raw_obj : DocumentFile) -> DocumentExtract:
        content = RfpRawBlobHander().get_path_pdf(raw_obj.location_path) # note this may need to change for other types.
        text_content = PdfParser().extract_text(content)
        raw_content = json.dumps(text_content)
        upload_path = f"{raw_obj.location_path}.extract.txt"
        container, blob_path = RfpExtractedTextBlobHander().upload(raw_content, upload_path)

        d = DocumentExtract(
            docfile=raw_obj,
            location_container=container,
            location_path=blob_path
        )
        d.save()
        return d


@job
def execute_rfp_parse(raw_doc_id : int):
    """This is our queued request."""
    RFPDocumentExtract().parse(raw_doc_id)
