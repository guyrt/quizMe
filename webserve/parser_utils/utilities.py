import bs4
from urllib.parse import urlparse


def parse_contents(content : str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(content, 'html')


def parse_file(local_path : str) -> bs4.BeautifulSoup:
    return parse_contents(open(local_path, 'r').read())


def get_rough_article_content(dom : bs4.BeautifulSoup) -> str:
    """Get a string from an article. Only returns the content of first <article> tag."""
    article = dom.find('article')
    if article:
        return article.get_text()
    return ""
