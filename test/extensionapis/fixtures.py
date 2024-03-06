import pytest
from extensionapis.models import RawDocCapture, SingleUrl
from mixer.backend.django import mixer


@pytest.fixture
def single_url_factory(existing_user):
    def create_single_url(host):
        url = f"https://{host}/index.html"
        su = mixer.blend(SingleUrl, user=existing_user, url=url, host=host)
        mixer.blend(
            RawDocCapture,
            user=existing_user,
            url=url,
            location_container="lc",
            location_path="lcp",
            url_model=su,
        )
        return su

    return create_single_url
