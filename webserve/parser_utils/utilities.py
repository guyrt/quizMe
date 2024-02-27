import bs4
from extensionapis.models import RawDocCapture

import logging

logger = logging.getLogger("default")


def parse_contents(content: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(content, "lxml")


def parse_file(local_path: str) -> bs4.BeautifulSoup:
    return parse_contents(open(local_path, "r").read())


def get_rough_article_content(raw_doc: RawDocCapture, dom: bs4.BeautifulSoup) -> str:
    """Get a string from an article. Only returns the content of first <article> tag."""

    url_facts = raw_doc.url_model.singleurlfact_set.all()
    url_facts_d = {u.fact_key: u.fact_value for u in url_facts}

    if url_facts_d.get("client_classification", "") == "article":
        reason = url_facts_d.get("client_reason")
        if reason == "hasArticleTag":
            article = dom.find("article")
            if article:
                return article.get_text()
        elif reason == "id":
            id_label = url_facts_d.get("client_idLookup")
            if id_label:
                article = dom.find(id=id_label)
                if article:
                    return article.get_text()
        elif reason == "class":
            class_label = url_facts_d.get("client_classLookup")
            if class_label:
                article = dom.find(class_=class_label)
                if article:
                    return article.get_text()
        else:
            logger.info("Get default content for quiz on %s", raw_doc.pk)
            return dom.get_text(separator=" ", strip=True)
        logger.warn(
            "Unable to find an article for raw_doc %s. This is unexpected.", raw_doc.pk
        )
    else:
        logger.warn("Asked to make a quiz for %s which is not an article.", raw_doc.pk)

    return dom.get_text(separator=" ", strip=True)
