import json
from azurewrapper.rfp.extractedtext_handler import RfpExtractedTextBlobHander
from django_rq import job
from dataclasses import asdict, replace
from mltrack.models import PromptResponse

from privateuploads.models import DocumentExtract, DocumentFile

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt, Prompt, PromptCell
from azurewrapper.gate import Gate

from rfp_utils.rfp_research.prompts import build_prompts

from typing import List


class RFPPromptRunner:

    def __init__(self) -> None:
        self._oai = OpenAIClient(engine='GPT-4-32K-0314', temp=0.9)  # todo make this a setting....
        self._gate = Gate(1)

    def execute(self, doc_extract_id : int):
        doc = DocumentExtract.objects.get(id=doc_extract_id)
        raw_content = RfpExtractedTextBlobHander(doc.location_container).get_path(doc.location_path)
        content = self._get_doc_content(raw_content)

        for prompt in build_prompts():
            results = self._run_prompt(prompt, content)
            self._process_results(doc, prompt, results)

    def _get_doc_content(self, payload_s : str):
        payload = json.loads(payload_s)
        if not hasattr(payload, 'get'):
            return " ".join(payload)
        format = payload.get('format')
        if format == 'list_str':
            return ' '.join(payload['content'])
        raise ValueError(f"Unepected doc format {format}")

    def _process_results(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        """Handle results - rely on versions to differentiate logic where necessary"""
        if prompt.name == "RFPSummarizeAsk" and prompt.version >= 2:
            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='longsummary',
                result=results[0]['response'],
                prompt_tokens=results[0]['prompt_tokens'],
                completion_tokens=results[0]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role='shortsummary',
                result=results[1]['response'],
                prompt_tokens=results[1]['prompt_tokens'],
                completion_tokens=results[1]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()
        elif prompt.name == 'RFPExtractDetails':
            self._deepdive_extract(doc, prompt, results)
        else:
            # we'll have to break this apart as we get more special cases.
            role = {
                'RFPExtractDetails': 'req_details',
                'RFPSpecificDates': 'specific_dates',
                'RFPLegal': 'legal_notes',
                'RFPCertifications': 'certifications',
                'RFPExpertise': 'expertise',
                'RFPVendors': 'vendors',
                'RFPQA': 'suggested_questions'
            }[prompt.name]

            r = PromptResponse(
                template_name=prompt.name,
                template_version=prompt.version,
                output_role=role,
                result=results[-1]['response'],
                prompt_tokens=results[-1]['prompt_tokens'],
                completion_tokens=results[-1]['completion_tokens']
            )
            r.save()
            r.document_inputs.add(doc)
            r.save()

    def _deepdive_extract(self, doc : DocumentExtract, prompt : Prompt, results : List[str]):
        """Parse results, get more details, and produce a link from main table to the subset.
        
        Each detail section is a PromptResponse of new type."""
        pass

    def _run_prompt(self, prompt : Prompt, doc) -> List[str]:
        prompt = replace(prompt)
        raw_responses = []
        current = fill_prompt(prompt, {'doc_content': doc})
        
        self._gate.gate()
        messages = [asdict(c) for c in current.content]
        raw_response_d = self._oai.call(messages, prompt.temp)

        raw_response = {
            'response': raw_response_d['response'],
            'prompt_tokens': raw_response_d['tokens']['prompt_tokens'],
            'completion_tokens': raw_response_d['tokens']['completion_tokens']
        }
        messages.append(asdict(PromptCell(role='assistant', content=raw_response_d['response'])))

        raw_responses.append(raw_response)
        while prompt.continuations:
            c = prompt.continuations.pop(0)
            messages.append(asdict(c))
            self._gate.gate()
            raw_response_d = self._oai.call(messages)

            raw_response = {
                'response': raw_response_d['response'],
                'prompt_tokens': raw_response_d['tokens']['prompt_tokens'],
                'completion_tokens': raw_response_d['tokens']['completion_tokens']
            }
            raw_responses.append(raw_response)
            messages.append(asdict(PromptCell(role='assistant', content=raw_response_d['response'])))

        return raw_responses


@job
def gpt_extract(raw_docextracts : List[int], doc_file_id):
    doc_file = DocumentFile.objects.get(id=doc_file_id)
    doc_file.processing_status = 'active'
    doc_file.save()

    try:
        pr = RFPPromptRunner()
        for raw_docextract in raw_docextracts:
            pr.execute(raw_docextract)
    except:
        doc_file.processing_status = 'error'
        doc_file.save()
    else:
        doc_file = DocumentFile.objects.get(id=doc_file_id)
        doc_file.processing_status = 'done'
        doc_file.save()
