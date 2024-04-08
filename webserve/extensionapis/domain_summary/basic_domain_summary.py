from typing import Dict, Iterable, List
from urllib.parse import urlparse

from ..models import SingleUrl


def summarize_domain(single_url: SingleUrl):
    other_urls = (
        SingleUrl.objects.filter(user=single_url.user, active=1)
        .exclude(id=single_url.pk)
        .filter(host=single_url.host)
        .order_by("-date_added")
    )

    single_urls_with_title = other_urls.annotate_with_titles()

    return _url_grouping_general(single_url.host, single_urls_with_title)


def _url_grouping_general(host: str, urls_with_titles: Iterable[SingleUrl]):
    if host == "github.com":
        return group_github(urls_with_titles)

    # default return.
    return [
        {
            "title": "__default__",
            "head": host,
            "urls": list(urls_with_titles[:5]),
        }
    ]


def group_ms_learn(urls_with_titles: Iterable[SingleUrl]):
    # basic limit on return size
    urls_with_titles = urls_with_titles[:100]

    # do a recursive clustering.


def group_github(urls_with_titles: Iterable[SingleUrl]):
    homepages: List[SingleUrl] = []
    group_pages: List[SingleUrl] = []  # github.com/guyrt
    projects: Dict[
        str, List[Dict]
    ] = {}  # project root like github.com/guyrt/project  map to List[urls with titles]

    # Do basic grouping
    for page in urls_with_titles:
        path_prefix, _ = get_path_root(page.url)
        # eliminate login
        if path_prefix.startswith("sessions"):
            continue

        if path_prefix == "":
            homepages.append(page)
        elif "/" not in path_prefix:
            group_pages.append(page)
        else:
            if path_prefix not in projects:
                projects[path_prefix] = []
            projects[path_prefix].append(page)

    project_clusters = []
    if len(homepages) > 0:
        # TODO for each homepage, get shortest url including path.
        project_clusters.append(
            {
                "title": homepages[0].recent_title,
                "head": homepages[0].url,
                "urls": homepages,
            }
        )

    if len(group_pages) > 0:
        project_clusters.append(
            {
                "title": "People and Organizations",
                "head": "https://github.com",
                "urls": dedupe_github_group_pages(group_pages),
            }
        )

    # For each project, cluster and sort. Choose shortest path for the head
    for project_name, pages in projects.items():
        min_item = dict_argmin(pages, lambda x: len(x.url))

        _, project_url = get_path_root(min_item.url)
        project_clusters.append(
            {"title": min_item.recent_title, "head": project_url, "urls": pages[:5]}
        )

    return project_clusters


def dedupe_github_group_pages(group_pages: Iterable[SingleUrl]):
    ret_list: List[SingleUrl] = []
    ret_set = set()
    for page in group_pages:
        _, short_url = get_path_root(page.url, depth=100)
        if short_url not in ret_set:
            ret_list.append(page)
            ret_set.add(short_url)
    return ret_list


def dict_argmin(lst, key):
    min = 10000000000000000000
    argmin = None
    for item in lst:
        key_item = key(item)
        if key_item < min:
            min = key_item
            argmin = item
    return argmin


def get_path_root(url, depth=2):
    parsed_url = urlparse(url)
    path = parsed_url.path
    path_segments = path.split("/")
    path_segments = [segment for segment in path_segments if segment]
    path_prefix = "/".join(path_segments[:depth])
    url_prefix = f"{parsed_url.scheme}://{parsed_url.netloc}/{path_prefix}"
    return path_prefix, url_prefix
