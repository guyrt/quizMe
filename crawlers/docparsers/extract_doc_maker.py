from bs4 import BeautifulSoup, Comment


def print_result_decorator(func):
    def wrapper(*args, **kwargs):
        # Do something before the function is called
        result = func(*args, **kwargs)
        print(f"{func} return {result}")
        return result
    return wrapper


@print_result_decorator
def try_find_creating_software(dom : BeautifulSoup, doc_type : str) -> str:
    
    # Strategy: look at comments for known maker
    comments = dom.find_all(text=lambda text:isinstance(text, Comment))

    for comment in comments:
        data = comment.string
        if 'Toppan Merrill' in data:
            return "Toppan Merrill Bridge"
        if 'Workiva' in data:
            return "Workiva"
        if 'CompSci Transform' in data:
            return "CompSci Transform"

    if doc_type.lower() in ['10-q', '10-k']:
        # return a default structured data parser
        return "Workiva"

    return "Default"
