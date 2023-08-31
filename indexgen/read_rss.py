from dataclasses import dataclass
import feedparser
import requests
from datetime import datetime
from time import mktime
import json

from common import headers

rss_url = "https://www.sec.gov/Archives/edgar/usgaap.rss.xml"


@dataclass(slots=True)
class SecDocRssEntry:
    doc_type: str  # 8-k ect
    title : str
    zip_link : str
    published : datetime
    id : str   # usually the file name.
    cik : str
    xbrl_json_str : str
    company_name : str
    edgar_assistantdirector : str


def get_all_entries():

    response = requests.get(rss_url, headers=headers)

    feed = feedparser.parse(response.content)

    for entry in feed.entries:
        zip_link_ = [l for l in entry.links if l['type'] == 'application/zip']
        if zip_link_:
            zip_link = zip_link_[0]['href']
        
        try:
            yield SecDocRssEntry(
                doc_type=entry.edgar_formtype or entry.summary,
                title=entry.title,
                zip_link=zip_link,
                published=datetime.fromtimestamp(mktime(entry.published_parsed)),
                id=entry.id,
                cik=entry.edgar_ciknumber,
                xbrl_json_str=json.dumps(entry.edgar_xbrlfile),
                company_name=entry.edgar_companyname,
                edgar_assistantdirector=entry.get('edgar_assistantdirector')
            )
        except AttributeError as e:
            print(e)
            print(f"Entry is {entry}")


if __name__ == "__main__":
    for row in get_all_entries():
        print(row)
