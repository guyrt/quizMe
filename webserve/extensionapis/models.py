from django.db import models, transaction
from django.core.exceptions import ValidationError
from azurewrapper.freeassociate.rawdoc_handler import RawDocCaptureHander

from extensionapis.managers import SingleUrlQuerySet
from users.models import User

from webserve.mixins import ModelBaseMixin


class SingleUrl(ModelBaseMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=2048)
    host = models.CharField(max_length=512)

    objects = SingleUrlQuerySet.as_manager()

    def get_corresponding_raw_docs(self):
        return RawDocCapture.objects.filter(url_model=self).order_by("-capture_index")
    
    def get_dom_classification(self):
        return SingleUrlFact.objects.filter(base_url=self)

    def __str__(self):
        return self.url + " - " + self.host

    class Meta:
        unique_together = ("user", "url")


class RawDocCapture(ModelBaseMixin):
    """Single impression."""

    # Record the capture index within an impression. Always prefer higher number
    capture_index = models.BigIntegerField(default=0, null=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=2048)
    title = models.CharField(max_length=1024)

    location_container = models.CharField(max_length=64)
    location_path = models.CharField(max_length=256)

    reader_location_container = models.CharField(max_length=64)
    reader_location_path = models.CharField(max_length=256)

    url_model = models.ForeignKey(SingleUrl, on_delete=models.CASCADE, null=True)

    def get_content(self, get_reader=False) -> str:
        """get_reader=True means try to get the reader."""
        if get_reader:
            container = self.reader_location_container
            path = self.reader_location_path
            if container == "" or path == "":
                return ""

        else:
            container = self.location_container
            path = self.location_path

        handler = RawDocCaptureHander(container_name=container)
        content = handler.download(self.user, path)
        return content

    def get_content_prefer_readable(self) -> str:
        reader_content = self.get_content(True)
        if reader_content != "":
            return reader_content
        return self.get_content(False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # When adding a new record, simply save it.
            super().save(*args, **kwargs)
        else:
            with transaction.atomic():
                # Lock the table to prevent race conditions.
                latest_version = (
                    RawDocCapture.objects.filter(id=self.pk)
                    .select_for_update()
                    .aggregate(max_capture_index=models.Max("capture_index"))[
                        "max_capture_index"
                    ]
                )
                if latest_version is not None and self.capture_index <= latest_version:
                    raise ValidationError(
                        f"Version must be greater than {latest_version}."
                    )
                super().save(*args, **kwargs)


class SingleUrlFact(ModelBaseMixin):
    """TODO: Right now, deleting a fact is not supported. Need to version or timestamp them.

    Consider adding a read timer and an offline process to clean up?"""

    base_url = models.ForeignKey(SingleUrl, on_delete=models.CASCADE)

    fact_key = models.CharField(max_length=64)
    fact_value = models.CharField(max_length=512)

    class Meta:
        unique_together = ("base_url", "fact_key")


class ObservedLink(ModelBaseMixin):
    """Track an observed link between pages."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_str = models.CharField(max_length=2028)
    from_obj = models.ForeignKey(
        SingleUrl, on_delete=models.SET_NULL, null=True, related_name="source"
    )

    to_str = models.CharField(max_length=2048)
    to_obj = models.ForeignKey(
        SingleUrl, on_delete=models.SET_NULL, null=True, related_name="target"
    )

    class Meta:
        unique_together = ("user", "from_str", "to_str")
