import pytest
from mixer.backend.django import mixer
from quizzes.models import SimpleQuiz

pytestmark = pytest.mark.django_db


@pytest.fixture
def mixed_quiz():
    """
    dummy example. mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    return mixer.blend(SimpleQuiz, content="lorem ipsum dolor")


def test_sanity(mixed_quiz):
    # load the fixture quiz
    sq = SimpleQuiz.objects.get(content="lorem ipsum dolor")
    # change the content attribute
    sq.content = "pig latin"
    # re-save
    sq.save()
    # confirm it saved as expected
    sq.refresh_from_db()
    assert sq.content == "pig latin"
