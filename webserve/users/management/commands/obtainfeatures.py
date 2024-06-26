from typing import List
from django.core.management.base import BaseCommand
from parser_utils.utilities import parse_contents
from extensionapis.models import SingleUrl
from bs4 import BeautifulSoup
import json


class Command(BaseCommand):
    help = "Collect features of pages accessed/stored. Usage: python manage.py obtainfeatures <PATH TO SAVE FEATURES>"

    def add_arguments(self, parser):
        parser.add_argument("data_path", type=str, help="Path to save feature data")
        parser.add_argument("--include_url", action="store_true", help="include doc url in output file")


    def handle(self, *args, **options):
        filename = options["data_path"]

        with open(filename, "w") as file:
            usr_host = SingleUrl.objects.all()
            for item in usr_host:
                related_docs = item.get_corresponding_raw_docs()[:1]
                doc_class = item.get_dom_classification()
                dom_class = ""

                for i in doc_class:
                    dom_class = i.fact_value
                    break  # Dom class is the first value

                for doc in related_docs:
                    try:
                        text = doc.get_content_prefer_readable()
                    except ValueError:
                        print(f"Warning - skipping {doc.id}")
                        break

                    raw_dom = parse_contents(text)
                    
                    if options["include_url"]:
                        features = self.transform_jsonl(
                            self.process_features(raw_dom, doc.url), dom_class, doc.url
                        )
                    else:
                        features = self.transform_jsonl(
                            self.process_features(raw_dom, doc.url), dom_class, None
                        )

                    file.write(json.dumps(features) + "\n")
                    print(f"Ran on {doc.id}")
                    break  # get only latest capture

    def process_features(self, document: str, url: str) -> List[any]:
        dashes = self.count_dashes_in_url(url)
        slashes = self.count_slashes_in_url(url)
        p_tags = self.count_p_tags(document)
        article_tags = self.count_article_tags(document)
        iframe_tags = self.count_iframe_tags(document)
        embed_tags = self.count_embed_tags(document)
        blockquote_tags = self.count_blockquote_tags(document)

        return [
            dashes,
            slashes,
            p_tags,
            article_tags,
            iframe_tags,
            embed_tags,
            blockquote_tags,
        ]

    def count_dashes_in_url(self, url: str) -> int:
        return url.count("-")

    def count_article_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("article"))

    def count_p_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("p"))

    def count_iframe_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("iframe"))

    def count_embed_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("embed"))

    def count_blockquote_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("blockquote"))

    def count_slashes_in_url(self, url: str) -> int:
        return url.count("/")

    def count_section_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("section"))

    def transform_jsonl(self, feature_list: [int], label: str, url:str|None) -> dict:
        classification = 0
        if label == "article":
            classification = 1

        if url is not None:
            return {
                "num_dashes": feature_list[0],
                "num_slashes": feature_list[1],
                "num_p_tags": feature_list[2],
                "num_article_tags": feature_list[3],
                "num_iframe_tags": feature_list[4],
                "num_embed_tags": feature_list[5],
                "num_blockquote_tags": feature_list[6],
                "label": classification,
                "url":url
            }
        
        return {
            "num_dashes": feature_list[0],
            "num_slashes": feature_list[1],
            "num_p_tags": feature_list[2],
            "num_article_tags": feature_list[3],
            "num_iframe_tags": feature_list[4],
            "num_embed_tags": feature_list[5],
            "num_blockquote_tags": feature_list[6],
            "label": classification,
        }
