from bs4 import BeautifulSoup, Comment

def try_find_creating_software(dom : BeautifulSoup) -> str:
    
    # Strategy: look at comments for known maker
    comments = dom.find_all(text=lambda text:isinstance(text, Comment))

    for comment in comments:
        data = comment.string
        if 'Toppan Merrill' in data:
            return "Toppan Merrill Bridge"
        if 'Workiva' in data:
            return "Workiva"

    return "Default"
