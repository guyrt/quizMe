from typing import List, Dict

from indexgen.localtypes import SecDocRssEntry


class StructuredDataHandler:

    def handle(self, structured_data: List[Dict[str, any]], summary : SecDocRssEntry):
        """Handle all structured data"""
        # get the key components and hash them to an id.
        # CIK, startdate, enddate, instant, ixName

        key_suffix = '_'.join(structured_data.get(k, '') for k in ['startDate', 'endDate', 'instant', 'ixName'])
        raw_key = f"{summary.cik}_{key_suffix}"
        for row in structured_data:
            row['cik'] = summary.cik
            row['docdate'] = str(summary.published)

        # upload
