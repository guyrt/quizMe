import bs4


def parse_file(local_path : str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(open(local_path, 'r').read(), 'lxml')
