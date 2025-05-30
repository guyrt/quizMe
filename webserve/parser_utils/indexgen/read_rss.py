import bs4
import requests
from datetime import datetime
from typing import List

from .common import headers
from .localtypes import EdgarFile, SecDocRssEntry

rss_url = "https://www.sec.gov/Archives/edgar/usgaap.rss.xml"


def get_all_entries():
    response = requests.get(rss_url, headers=headers)
    for row in _extract_dom(response.content):
        yield row


def get_local_entries(filename):
    content = open(filename, "r").read()
    for row in _extract_dom(content):
        yield row


def _extract_dom(content):
    dom = bs4.BeautifulSoup(content, features="xml")
    entries = dom.find_all("item")

    for entry in entries:
        title = _safe_get_key(entry, "title")

        zip_link_ = entry.find_next("enclosure", attrs={"type": "application/zip"})
        if zip_link_:
            zip_link = zip_link_.attrs["url"]
        else:
            raise AttributeError(f"No zip link for {title}")

        try:
            yield SecDocRssEntry(
                doc_type=_safe_get_key(entry, "edgar:formType"),
                title=title,
                zip_link=zip_link,
                published=_get_published_time(entry),
                id=_safe_get_key(entry, "guid"),
                cik=_safe_get_key(entry, "edgar:cikNumber"),
                edgar_files=_make_files(entry),
                company_name=_safe_get_key(entry, "edgar:companyName"),
                edgar_assistantdirector=_safe_get_key(entry, "edgar:assistantDirector"),
            )
        except AttributeError as e:
            print(e)
            print(f"Entry is {entry}")
        except Exception as e:
            print(e)
            print(f"Entry is {entry}")
            break


def _make_files(entry: bs4.element.Tag) -> List[EdgarFile]:
    return [
        EdgarFile(
            filename=e.attrs["edgar:file"],
            filetype=e.attrs["edgar:type"],
            url=e.attrs["edgar:url"],
        )
        for e in entry.find_all("edgar:xbrlFile")
    ]


def _get_published_time(entry: bs4.element.Tag) -> datetime:
    dt_str = _safe_get_key(entry, "edgar:acceptanceDatetime")
    return datetime.strptime(dt_str, "%Y%m%d%H%M%S")


def _safe_get_key(entry: bs4.element.Tag, key: str) -> str:
    elt = entry.find_next(key)
    if not elt:
        #        print(f"Element {key} not found in {entry}")
        return ""
    return elt.string


if __name__ == "__main__":
    for row in get_all_entries():
        print(row)
