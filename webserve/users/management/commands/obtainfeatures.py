from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth import get_user_model
from extensionapis.models import RawDocCapture, SingleUrl
from quizzes.models import get_simple_quiz, SimpleQuizResults
from quizzes.schemas import SimpleQuizSchema, UploadQuizResultsSchema
from users.models import User
import re 

# User = get_user_model()


class Command(BaseCommand):
    help = "Obtain and store pageFeatures"

    def handle(self, *args, **options):

        #first get user page from Single 
        # SingleUrl.objects.
        # f
        self.stdout.write("About to get to a")
        # self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
        # a = SingleUrl.objects.all()
        a = RawDocCapture.objects.all()[:5]
    
        self.stdout.write(self.style.SUCCESS('5 entries in the database:'))
        for item in a:
                self.stdout.write(f'Item {item.url}, {item.host}')
       
        self.stdout.write(  self.style.SUCCESS('Successfully closed poll "%s"' % a))
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

    def count_article_tags(self,html_content: str) -> int:
        return len(re.findall(r'<article\b[^>]*>(.*?)</article>', html_content, re.DOTALL))

    def count_p_tags(self, html_content: str) -> int:
        return len(re.findall(r'<p\b[^>]*>(.*?)</p>', html_content, re.DOTALL))

    def count_iframe_tags(self, html_content: str) -> int:
        return len(re.findall(r'<iframe\b[^>]*>(.*?)</iframe>', html_content, re.DOTALL))

    def count_embed_tags(self, html_content: str) -> int:
        """Counts the number of <embed> tags in the HTML content."""
        return len(re.findall(r'<embed\b[^>]*>(.*?)</embed>', html_content, re.DOTALL))

    def count_blockquote_tags(self, html_content: str) -> int:
        return len(re.findall(r'<blockquote\b[^>]*>(.*?)</blockquote>', html_content, re.DOTALL))

    def count_slashes_in_url(self, url: str) -> int:
        return url.count('/')

    def count_section_tags(self, html_content: str) -> int:
        return len(re.findall(r'<section\b[^>]*>(.*?)</section>', html_content, re.DOTALL))
