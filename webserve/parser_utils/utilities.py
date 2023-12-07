import bs4
from urllib.parse import urlparse


def parse_contents(content : str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(content, 'xml')


def parse_file(local_path : str) -> bs4.BeautifulSoup:
    return parse_contents(open(local_path, 'r').read())
