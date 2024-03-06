from unittest.mock import MagicMock
import pytest
from extensionapis.models import SingleUrl
from extensionapis.jobs import handle_new_domain_remove
from _pytest.monkeypatch import MonkeyPatch


from .fixtures import existing_url, existing_user  # These are used...

pytestmark = pytest.mark.django_db



@pytest.fixture()
def set_djangorq(monkeypatch: MonkeyPatch):
    mock_enqueue = MagicMock()

    monkeypatch.setattr("extensionapis.jobs.enqueue", mock_enqueue)
    yield mock_enqueue


def test_drop_url(existing_url : SingleUrl, set_djangorq):
    handle_new_domain_remove("existing.com")
    assert 2 == set_djangorq.call_count
    assert 0 == SingleUrl.objects.filter(pk=existing_url.pk).count()
