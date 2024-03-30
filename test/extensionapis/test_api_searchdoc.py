import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import MagicMock

from extensionapis.api import router
from extensionapis.models import RawDocCapture
from mltrack.search.relevant_chunks import DocumentSearchResponse, NoChunksError

from ..users.fixtures import existing_user, TestClientWithDefaultHeaders  # noqa
from .fixtures import single_url_factory  # noqa


pytestmark = pytest.mark.django_db


@pytest.fixture()
def api_client():
    client = TestClientWithDefaultHeaders(router)
    yield client


@pytest.fixture()
def return_some_matches(monkeypatch: MonkeyPatch):
    mock_docs = MagicMock()
    mock_docs.return_value = [
        DocumentSearchResponse(
            doc_id="c1bd1057-d1c6-4457-ae87-261e3a262ce6",
            doc_url="test.com/test",
            score=0.1,
            chunk="chunk",
        )
    ]

    monkeypatch.setattr("extensionapis.api.find_relevant_docs", mock_docs)
    yield mock_docs


@pytest.fixture()
def throw_no_matches(monkeypatch: MonkeyPatch):
    def _raise(*args, **kwargs):
        raise NoChunksError()

    mock_docs = MagicMock(side_effect=_raise)

    monkeypatch.setattr("extensionapis.api.find_relevant_docs", mock_docs)
    yield mock_docs


def test_searchdoc_some_docs(single_url_factory, api_client, return_some_matches):  # noqa
    single_url_factory("test.com")
    rdc = RawDocCapture.objects.get()  # created in the fixture.

    response = api_client.get(f"/rawdoccaptures/{rdc.pk}/docsearch")
    assert 200 == response.status_code

    response_json = response.json()
    assert "c1bd1057-d1c6-4457-ae87-261e3a262ce6" == response_json[0]["doc_id"]


def test_searchdoc_wait(single_url_factory, api_client, throw_no_matches):  # noqa
    single_url_factory("test.com")
    rdc = RawDocCapture.objects.get()  # created in the fixture.

    response = api_client.get(f"/rawdoccaptures/{rdc.pk}/docsearch")
    assert 202 == response.status_code

    response_json = response.json()
    assert "wait" == response_json["status"]
