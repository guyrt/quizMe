import bs4

from typing import List


def merge_tables_of_requirements(tables : List[bs4.BeautifulSoup]):
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
    
    return_rows = []

    for row in all_rows:
        contents = [r for r in row.text.split('\n') if r]
        req = contents[0]
        section = contents[1]

        return_rows.append({'req': req, 'section': section})

    return return_rows
