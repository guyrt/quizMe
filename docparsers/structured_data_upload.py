from typing import List, Dict
from azurewrapper.cosmos_sec_facts import CosmosDbSecFactsHander

from indexgen.localtypes import SecDocRssEntry


class StructuredDataHandler:

    def __init__(self, cdb_handler : CosmosDbSecFactsHander) -> None:
        self._cbd_handler = cdb_handler

    def handle(self, structured_data: List[Dict[str, any]], summary : SecDocRssEntry):
        """Handle all structured data"""
        # get the key components and hash them to an id.
        # CIK, startdate, enddate, instant, ixName

        primary_key = ['startDate', 'endDate', 'instant', 'ixName']
        print(f"Found {len(structured_data)} facts to upload")
        for row in structured_data:
            key_suffix = '_'.join(row.get(k, '') for k in primary_key)
            raw_key = f"{summary.cik}_{key_suffix}"

            row['cik'] = summary.cik
            row['docdate'] = summary.published
            row['id'] = raw_key

            # upload
            self._cbd_handler.write(row)
