import pytest
from extensionapis.models import RawDocCapture, SingleUrl
from users.models import User
from mixer.backend.django import mixer


@pytest.fixture
def existing_user(scope="module"):
    """
    Dummy example. Mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    yield mixer.blend(User, email="exists@user.com")


@pytest.fixture
def existing_url(existing_user, scope="module"):
    url = "https://www.existing.com/index.html"
    host = "www.existing.com"
    su = mixer.blend(SingleUrl, user=existing_user, url=url, host=host)
    mixer.blend(
        RawDocCapture,
        user=existing_user,
        url=url,
        location_container="lc",
        location_path="lcp",
        url_model=su,
    )
    yield su
