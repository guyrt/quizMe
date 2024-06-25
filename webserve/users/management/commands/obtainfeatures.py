from django.core.management.base import BaseCommand, CommandError
from parser_utils.utilities import get_rough_article_content, parse_contents
from django.contrib.auth import get_user_model
from extensionapis.models import RawDocCapture, SingleUrl
from quizzes.models import get_simple_quiz, SimpleQuizResults
from quizzes.schemas import SimpleQuizSchema, UploadQuizResultsSchema
from users.models import User
import re 
from bs4 import BeautifulSoup
import json

# User = get_user_model()


class Command(BaseCommand):
    help = "Obtain and store pageFeatures"


    def args (self, parser):
            parser.add_argument("data_path", nargs="1", type=str, help="Path to save feature data")
            

    def handle(self,  *args, **options):

        filename="./test.jsonl"

        #first get user page from Single 
        # SingleUrl.objects.
        # f
        
        # self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
        # a = SingleUrl.objects.all()
        usr_host = SingleUrl.objects.all()
        for item in usr_host:
                self.stdout.write(f'Current Entry {item.url}, {item.host}')
                related_docs = item.get_corresponding_raw_docs()
                doc_class = item.get_dom_classification()
                for i in doc_class:
                     self.stdout.write(f'element {i.fact_value}')
                self.stdout.write(f'Classification: {doc_class}')
                for doc in related_docs:
                     raw_dom = parse_contents(doc.get_content_prefer_readable())
                     features = self.transform_jsonl(self.process_features(raw_dom, doc.url))
                     self.stdout.write(f'Related RawDoc Features: {features}')
                     
                    #  self.stdout.write(f'Related RawDoc Features: {features} ; url: {doc.url}') #here I get the url; I just need to get the content and trigger 
                                                                   #function
                
        '''
        b = RawDocCapture.objects.all()[:5]
        self.stdout.write(self.style.SUCCESS('Content:'))

        # if options["data_path"]:
        #      filename = options["data_path"]
 
        with open(filename, 'w') as file:
            for raw_doc in b:
                    raw_dom = parse_contents(raw_doc.get_content_prefer_readable())
                    # article_content = get_rough_article_content(raw_doc, raw_dom)
                    # self.stdout.write(f'{raw_dom}')
                    features = self.process_features(raw_dom, raw_doc.url)
                    
                    file.write(json.dumps(self.transform_jsonl(features)) + '\n')
            self.stdout.write(f'Done Processing data')
        '''
        # self.process_features()

    def process_features(self, document:str, url:str) -> [int]:

        dashes = self.count_dashes_in_url(url)
        slashes = self.count_slashes_in_url(url)
        p_tags = self.count_p_tags(document)
        article_tags = self.count_article_tags(document)
        iframe_tags = self.count_iframe_tags(document)
        embed_tags = self.count_embed_tags(document)
        blockquote_tags = self.count_blockquote_tags(document)

        return [dashes, slashes, p_tags, article_tags, iframe_tags, embed_tags, blockquote_tags]
        
    def count_dashes_in_url(self, url: str) -> int:
        return url.count('-')

    def count_article_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('article'))

    def count_p_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('p'))

    def count_iframe_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('iframe'))

    def count_embed_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('embed'))

    def count_blockquote_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('blockquote'))

    def count_slashes_in_url(self, url: str) -> int:
        return url.count('/')

    def count_section_tags(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all('section'))

    def transform_jsonl(self, feature_list: [int]) -> dict: 
        return {"num_dashes":feature_list [0],  
                "num_slashes":feature_list[1],
                "num_p_tags":feature_list[2],
                "num_article_tags":feature_list[3],
                "num_iframe_tags":feature_list[4],
                "num_embed_tags":feature_list[5],
                "num_blockquote_tags":feature_list[6]}