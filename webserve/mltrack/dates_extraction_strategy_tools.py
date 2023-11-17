import bs4
import re

from typing import Dict, List


def merge_tables_of_dates(tables : List[bs4.BeautifulSoup]):
    """Produce a List of dates and explanations. Merge common dates.
    
    Assume input is a set of tables with exactly two rows each:

    <tr>
        <td>2023-10-13</td>
        <td>Estimated Start of Contract (Subject to completion of Security Design Review)</td>
    </tr>
    """

    all_rows = []
    for table in tables:
        all_rows.extend(table.find('tbody').find_all('tr'))
    
    all_dates : Dict[str, List] = {}

    for row in all_rows:
        contents = [r for r in row.text.split('\n') if r]
        date_part = contents[0]
        meaning = contents[1]
        clean_date = format_date(date_part)
        if clean_date not in all_dates:
            all_dates[clean_date] = []
        all_dates[clean_date].append(meaning)

    # TODO - merge comments if they are near overlaps.
    all_dates = {k: '\n'.join(v) for k, v in all_dates.items()}
    return all_dates



# Define regex patterns for the three cases
pattern1 = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # yyyy-MM-dd
pattern2 = re.compile(r'^\d{4}-\d{2}-00$')     # yyyy-MM-00
pattern3 = re.compile(r'^\d{4}-\d{2}$')        # yyyy-MM
def format_date(date_str : str) -> str | None:
    """Accept three formats:

    yyyy-MM-dd
    yyyy-MM-00
    yyyy-MM

    otherwise return none. 
    """
    # Check and return based on the matching pattern
    if pattern2.match(date_str):
        return date_str[:7]  # return yyyy-MM
    elif pattern1.match(date_str) or pattern3.match(date_str):
        return date_str
    else:
        return None



"""
<table>
<thead>
<tr>
<th>Date</th>
<th>Meaning</th>
</tr>
</thead>
<tbody>
<tr>
<td>2023-08-25</td>
<td>Proposal Due Date</td>
</tr>
<tr>
<td>2023-10-13</td>
<td>Estimated Start of Contract (Subject to completion of Security Design Review)</td>
</tr>
<tr>
<td>2025-06-30</td>
<td>Estimated End of Contract (with possibility for extensions)</td>
</tr>
<tr>
<td>2023-07-12</td>
<td>Issuance of Request for Proposals</td>
</tr>
<tr>
<td>2023-07-25</td>
<td>Pre-Proposal Conference</td>
</tr>
<tr>
<td>2023-08-15</td>
<td>Deadline for submitting written questions</td>
</tr>
<tr>
<td>2023-08-18</td>
<td>OFM will issue responses</td>
</tr>
<tr>
<td>2023-08-25</td>
<td>Complaints due</td>
</tr>
<tr>
<td>2023-08-31</td>
<td>Deadline for submitting Proposal</td>
</tr>
<tr>
<td>2023-09-01</td>
<td>Start of OFM scoring of proposals</td>
</tr>
<tr>
<td>2023-09-19</td>
<td>End of OFM scoring of proposals</td>
</tr>
<tr>
<td>2023-09-25</td>
<td>Potential start of OFM to Hold Oral Presentation (if required)</td>
</tr>
<tr>
<td>2023-09-26</td>
<td>Potential end of OFM to Hold Oral Presentation (if required)</td>
</tr>
<tr>
<td>2023-09-28</td>
<td>OFM announces successful Applicants &amp; notifies unsuccessful Applicants</td>
</tr>
<tr>
<td>2023-10-03</td>
<td>Unsuccessful Applicants may request Debriefing until 3:30 p.m. Local Time, Olympia, WA</td>
</tr>
<tr>
<td>2023-10-13</td>
<td>Tentative Sign Agreements date (Subject to Security Design Review)</td>
</tr>
<tr>
<td>2024-04-00</td>
<td>Anticipated Completion of Design (One Washington Program Workday implementation - Phase 1A milestone)</td>
</tr>
<tr>
<td>2024-10-00</td>
<td>Anticipated End-to-End Testing (One Washington Program Workday implementation - Phase 1A milestone)</td>
</tr>
<tr>
<td>2024-12-00</td>
<td>Anticipated User Experience Review (One Washington Program Workday implementation - Phase 1A milestone)</td>
</tr>
<tr>
<td>2025-03-00</td>
<td>Anticipated Workday final release prior to Go Live (One Washington Program Workday implementation - Phase 1A milestone)</td>
</tr>
<tr>
<td>2025-07-00</td>
<td>Anticipated Go Live date (One Washington Program Workday implementation - Phase 1A milestone)</td>
</tr>
</tbody>
</table>
"""