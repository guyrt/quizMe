from unittest.mock import MagicMock
import pytest
from extensionapis.models import SingleUrl
from extensionapis.jobs import handle_new_domain_remove
from _pytest.monkeypatch import MonkeyPatch


from .fixtures import single_url_factory  # noqa
from ..users.fixtures import existing_user  # noqa

pytestmark = pytest.mark.django_db


@pytest.fixture()
def set_djangorq(monkeypatch: MonkeyPatch):
    mock_enqueue = MagicMock()

    monkeypatch.setattr("extensionapis.jobs.enqueue", mock_enqueue)
    yield mock_enqueue


def test_drop_url_by_suburl(single_url_factory: SingleUrl, set_djangorq):  # noqa
    existing_url = single_url_factory("b.a.com")
    handle_new_domain_remove("a.com")
    assert 2 == set_djangorq.call_count
    assert 0 == SingleUrl.objects.filter(pk=existing_url.pk).count()


def test_drop_url_exact(single_url_factory: SingleUrl, set_djangorq):  # noqa
    existing_url = single_url_factory("aa.com")
    handle_new_domain_remove("aa.com")
    assert 2 == set_djangorq.call_count
    assert 0 == SingleUrl.objects.filter(pk=existing_url.pk).count()


def test_drop_url_nodelete(single_url_factory: SingleUrl, set_djangorq):  # noqa
    existing_url = single_url_factory("aa.com")
    handle_new_domain_remove("a.com")
    assert 0 == set_djangorq.call_count
    assert 1 == SingleUrl.objects.filter(pk=existing_url.pk).count()


def test_drop_url_nodelete_suburl(single_url_factory: SingleUrl, set_djangorq):  # noqa
    existing_url = single_url_factory("a.com")
    handle_new_domain_remove("b.a.com")
    assert 0 == set_djangorq.call_count
    assert 1 == SingleUrl.objects.filter(pk=existing_url.pk).count()
