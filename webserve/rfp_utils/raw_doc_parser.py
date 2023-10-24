import json 

from azurewrapper.rfp.rawdocs_handler import RfpRawBlobHander
from azurewrapper.rfp.extractedtext_handler import RfpExtractedTextBlobHander
from privateuploads.models import RawUpload, DocumentFile
from webserve.rfp_utils.pdf_parser import PdfParser


class RFPDocumentExtract:

    def __init__(self) -> None:
        pass

    def parse(self, raw_doc_id : int):
        raw_obj = RawUpload.objects.get(id=raw_doc_id)

        doc_files = []

        # Step 1: extract the doc and save
        if raw_obj.format == 'pdf':
            doc_files.append(self._extract_pdf(raw_obj))
        else:
            raise NotImplementedError(f"RawUpload {raw_obj.pk}: {raw_obj.format}")

        # Step 2: queue up GPT parse
        

    def _extract_pdf(self, raw_obj : RawUpload) -> DocumentFile:
        content = RfpRawBlobHander().get_path(raw_obj.location_path)
        text_content = PdfParser().extract_text(content)
        raw_content = json.dumps(text_content)
        upload_path = f"{raw_obj.location_path}.extract.txt"
        doc_name = raw_obj.location_path.split()
        container, blob_path = RfpExtractedTextBlobHander().upload(raw_content, upload_path)

        d = DocumentFile(
            document=raw_obj.document,
            source=raw_obj,
            file_role='rfp', # for now, assume single doc is always RFP
            doc_format='pdf',
            doc_name=doc_name,
            location_container=container,
            location_path=blob_path,
            processing_status="notstarted",
            last_jobid=''
        )
        d.save()
        return d


def execute_rfp_parse(raw_doc_id : int):
    """This is our queued request."""
    RFPDocumentExtract().parse(raw_doc_id)
