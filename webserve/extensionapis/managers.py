from django.db import models
from django.db.models import OuterRef, Subquery


class SingleUrlQuerySet(models.QuerySet):
    def annotate_with_titles(self):
        from extensionapis.models import RawDocCapture

        most_recent_capture = RawDocCapture.objects.filter(
            url_model=OuterRef("pk")
        ).order_by("-date_added")

        # We use a subquery to get the title of the most recent capture
        recent_capture_title = most_recent_capture.values("title")[:1]

        # Now, annotate the SingleUrl queryset
        return self.annotate(recent_title=Subquery(recent_capture_title))
