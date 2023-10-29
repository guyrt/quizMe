import json
from django_rq import job, enqueue

from azurewrapper.rfp.rawdocs_handler import RfpRawBlobHander
from azurewrapper.rfp.extractedtext_handler import RfpExtractedTextBlobHander
from privateuploads.models import DocumentFile, DocumentExtract
from rfp_utils.pdf_parser import PdfParser
from rfp_utils.gpt_extract_rfp import gpt_extract


class RFPDocumentExtract:

    def __init__(self) -> None:
        pass

    def parse(self, doc_id : int):
        doc_file = DocumentFile.objects.get(id=doc_id)

        extracted_files = []

        # Step 1: extract the doc and save
        if doc_file.doc_format == 'pdf':
            extracted_files.append(self._extract_pdf(doc_file))
        else:
            raise NotImplementedError(f"RawUpload {doc_file.pk}: {doc_file.doc_format}")

        # remove existing and save
        DocumentExtract.objects.filter(docfile=doc_id).update(active=0)
        for de in extracted_files:
            de.save()

        # Step 2: queue up GPT parse
        result = enqueue(gpt_extract, [d.id for d in extracted_files], doc_file.id)
        doc_file.last_jobid = result.id
        doc_file.save()

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
        return d


@job
def execute_doc_parse(raw_doc_id : int):
    """This is our queued request."""
    RFPDocumentExtract().parse(raw_doc_id)
