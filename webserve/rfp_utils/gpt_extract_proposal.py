from azurewrapper.rfp.extractedtext_handler import RfpExtractedTextBlobHander

from privateuploads.models import DocumentExtract

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.gate import Gate

from rfp_utils.rfp_research.prompts import build_prompts

class ProposalPromptRunner:

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