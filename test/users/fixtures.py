import pytest
from users.models import User
from mixer.backend.django import mixer


@pytest.fixture
def existing_user():
    """
    Dummy example. Mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    return mixer.blend(User, email="exists@user.com")
