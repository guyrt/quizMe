from ..models import RawDocCapture, SingleUrl
from django.db.models import OuterRef, Subquery


def summarize_domain(single_url: SingleUrl):
    other_urls = (
        SingleUrl.objects.filter(user=single_url.user, active=1)
        .exclude(id=single_url.pk)
        .filter(host=single_url.host)
        .order_by("-date_added")
    )

    most_recent_capture = RawDocCapture.objects.filter(
        url_model=OuterRef("pk")
    ).order_by("-date_added")

    # We use a subquery to get the title of the most recent capture
    recent_capture_title = most_recent_capture.values("title")[:1]

    # Now, annotate the SingleUrl queryset
    single_urls_with_title = other_urls.annotate(
        recent_title=Subquery(recent_capture_title)
    )

    return _url_grouping_general(single_url.host, single_urls_with_title)


def _url_grouping_general(host: str, urls_with_titles):
    # default return.
    return [
        {
            "title": "__default__",
            "head": host,
            "urls": list(urls_with_titles[:5]),
        }
    ]
