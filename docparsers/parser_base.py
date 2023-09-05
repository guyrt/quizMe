import bs4


def parse_contents(content : str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(content, 'xml')


def parse_file(local_path : str) -> bs4.BeautifulSoup:
    return parse_contents(open(local_path, 'r').read())
