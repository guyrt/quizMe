import json
from django_rq import job, enqueue

from azurewrapper.rfp.rawdocs_handler import KMRawBlobHander
from azurewrapper.rfp.extractedtext_handler import KMExtractedTextBlobHander
from privateuploads.models import DocumentFile, DocumentExtract
from rfp_utils.pdf_parser import PdfParser
from rfp_utils.extract_task import gpt_extract

from typing import List


class KBDocumentExtract:

    def __init__(self) -> None:
        pass

    def parse(self, doc_file_id : int) -> List[int]:
        doc_file = DocumentFile.objects.get(id=doc_file_id)

        extracted_files = []

        # Step 1: extract the doc and save
        if doc_file.doc_format == 'pdf':
            extracted_files.append(self._extract_pdf(doc_file))
        else:
            raise NotImplementedError(f"RawUpload {doc_file.pk}: {doc_file.doc_format}")

        # remove existing and save
        DocumentExtract.objects.filter(docfile=doc_file_id).update(active=0)
        for de in extracted_files:
            de.save()

        return [de.pk for de in extracted_files]

    def _extract_pdf(self, raw_obj : DocumentFile) -> DocumentExtract:
        content = KMRawBlobHander().get_path_to_bytes(raw_obj.location_path) # note this may need to change for other types.
        parser = PdfParser()
        text_content = parser.extract_text(content)

        raw_content = json.dumps(text_content)
        upload_path = f"{raw_obj.location_path}.extract.txt"
        container, blob_path = KMExtractedTextBlobHander().upload(raw_content, upload_path)

        d = DocumentExtract(
            docfile=raw_obj,
            location_container=container,
            location_path=blob_path,
            structure='rawtext'
        )
        return d


@job
def execute_doc_parse(doc_cluster_id : int):
    """This is our queued request."""
    objs = DocumentFile.objects.filter(active=True).filter(document__id=doc_cluster_id)
    all_extracted_files = []
    for obj in objs:
        all_extracted_files.extend(KBDocumentExtract().parse(obj.id))

    enqueue(gpt_extract, all_extracted_files, doc_cluster_id)
