import os 
import requests

from indexgen.gate import Gate
from writer.tools.base import Tool


from dotenv import load_dotenv
load_dotenv()


class Bing(Tool):

    name = "bing_search"
    description = (
        "A wrapper around Bing Search. "
        "Useful to answer questions about current events including news. "
        "Provides less detail than wikipedia, but is more likely to contain "
        "information that is up to date. "
        "Is very helpful for specific questions. "
        "Input should be a search query. If you are asking for background information about a company's market "
        "or industry, do not include the company name in the search term. "
    )

    def __init__(self) -> None:
        self._subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
        self._endpoint = os.environ['BING_SEARCH_V7_ENDPOINT']
        self._gate = Gate(0.5)  # limit is 3qps in free tier.

    def run(self, query):
        # Construct a request
        self._gate.gate()

        mkt = 'en-US'
        params = { 'q': query, 'mkt': mkt, 'responseFilters': '-videos,-images,-places' }
        headers = { 'Ocp-Apim-Subscription-Key': self._subscription_key }

        # Call the API
        try:
            response = requests.get(self._endpoint, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as ex:
            raise ex
            