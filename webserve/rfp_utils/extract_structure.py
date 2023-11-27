from dataclasses import asdict
from typing import List, Tuple

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt
from azurewrapper.rfp.extractedtext_handler import KMExtractedTextBlobHander
from azurewrapper.rfp.rawdocs_handler import KMRawBlobHander
from django_rq import enqueue, job
from mltrack.models import PromptResponse
from privateuploads.models import DocumentExtract, DocumentFile
from rfp_utils.extract_task import gpt_extract
from rfp_utils.large_doc_splitter import LargeDocSplitter
from rfp_utils.pdf_parser import PdfParser
from rfp_utils.rfp_research.toc import table_of_contents_extract_prompt
from rfp_utils.json_utils import parse_json


class StructuredExtraction:
    """Structured extraction that uses models to extract a table of contents then leverages the TOC to find and classify
    sections."""

    def __init__(self) -> None:
        self._oai = OpenAIClient(model='gpt4', temp=0.9)

    def parse(self, doc_file_id : int) -> List[int]:
        doc_file = DocumentFile.objects.get(id=doc_file_id)

        extracted_files = []

        # Step 1: extract the doc
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
        text_content : List[str] = parser.extract_text(content)['content']
        raw_text = "\n".join(text_content)

        toc, structure = self._extract_structure(raw_text)
        structure_str = parse_json(structure)

        upload_path = f"{raw_obj.location_path}.extract.txt"
        container, blob_path = KMExtractedTextBlobHander().upload(structure_str, upload_path)

        d = DocumentExtract(
            docfile=raw_obj,
            location_container=container,
            location_path=blob_path,
            structure='sectionsv1'
        )
        d.save()

        toc.document_inputs.add(d)
        toc.save()
        structure.document_inputs.add(d)
        structure.save()
        return d

    def _extract_structure(self, raw_text : str) -> Tuple[PromptResponse, PromptResponse]:
        toc_response, parsed_toc = self._extract_table_of_contents(raw_text)
        sections_response = self._extract_sections_with_toc(parsed_toc, raw_text)
        return toc_response, sections_response
    
    def _extract_table_of_contents(self, raw_text) -> PromptResponse:
        """Simple, single-pass prompt"""
        prompt = table_of_contents_extract_prompt
        chunks = LargeDocSplitter(self._oai).split(raw_text, 1500)
        doc = chunks[0]
        current = fill_prompt(prompt, {'doc_content': doc})
        messages = [asdict(c) for c in current.content]

        response = self._oai.call(messages, temp=prompt.temp)
        import ipdb; ipdb.set_trace()
        parsed_response = parse_json(response['response'])

        pr = PromptResponse.objects.create(
            template_name=prompt.name,
            template_version=prompt.version,
            output_role='tocextract',
            result=response['response'],
            prompt_tokens=response['prompt_tokens'],
            completion_tokens=response['completion_tokens'],
            model_service=self._oai.api_type,
            model_name=self._oai.engine
        )
        return pr, parsed_response

    def _extract_sections_with_toc(self, toc, raw_text):
        pass



@job
def execute_doc_structure_parse(doc_cluster_id : int):
    """This is our queued request."""
    objs = DocumentFile.objects.filter(active=True).filter(document__id=doc_cluster_id)
    all_extracted_files = []
    for obj in objs:
        all_extracted_files.extend(StructuredExtraction().parse(obj.id))

    enqueue(gpt_extract, all_extracted_files, doc_cluster_id)
