import json 

from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from intelligence.embedder import Embedder
from azurewrapper.prompt_types import PromptResponse, promp_response_from_dict


class EmbeddingDriver:

    def __init__(self) -> None:
        self._doc_grabber = AzureParsedDocsBlobHandler()
        self._embedder = Embedder()

    def embed_from_cik(self, cik : str):
        files = list(self._get_files(cik))
        for f in files:
            lines = self._doc_grabber.get_path(f)
            for line in lines.splitlines():
                jl = promp_response_from_dict(json.loads(line))
                self._embed_response(jl)
                
    def _embed_response(self, line : PromptResponse):
        # TODO: decide whether to embed whole response or to split it.
        user_prompt = [c for c in line.prompt.content if c.role == 'user'][0]
        user_embed = self._embedder.embed(user_prompt.content)
        response_embed = self._embedder.embed(line.response)
        return user_embed, response_embed


    def _get_files(self, cik):
        for blob in self._doc_grabber.walk_blobs(cik, 'jsonl'):
            yield blob
