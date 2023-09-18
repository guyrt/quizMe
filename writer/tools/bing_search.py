import os
import requests

from azurewrapper.gate import Gate
from writer.tools.base import Tool


from dotenv import load_dotenv

from writer.writer_types import KnownFact, KnownFactInternal, KnownFactSource
load_dotenv()


class Bing(Tool):

    name = "bing_search"
    description = (
        "A wrapper around Bing Search. "
        "Useful to answer questions about current events including news. "
        "You should rewrite user's query to be shorter and more general. For example, if the user asks about 'industry size for nabisco' "
        "you should rewrite to something like 'industry size for cookies and snacks'."
        "Is very helpful for specific questions. "
        "Input should be a search query. "
    )

    def __init__(self) -> None:
        self._subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
        self._endpoint = os.environ['BING_SEARCH_V7_ENDPOINT']
        self._gate = Gate(0.5)  # limit is 3qps in free tier.

    def run(self, query):
        # Construct a request, execute, parse, and return a set of KnownFacts.
        self._gate.gate()

        mkt = 'en-US'
        params = { 'q': query, 'mkt': mkt, 'responseFilters': '-videos,-images,-places' }
        headers = { 'Ocp-Apim-Subscription-Key': self._subscription_key }

        # Call the API
        try:
            response = requests.get(self._endpoint, headers=headers, params=params)
            response.raise_for_status()
            self.create_known_facts(query, response.json())
        except Exception as ex:
            raise ex

    def create_known_facts(self, query, raw_response) -> KnownFact:

        known_facts = []
        for result in raw_response.get('webPages', dict()).get('value', list()):  # list of responses.
            kf = KnownFact(
                value=result['value']['snippet'],
                source=KnownFactSource(
                    source_type='bing',
                    value=result['url']
                ),
                internal=KnownFactInternal(
                    query=query
                )
            )
            known_facts.append(kf)