import os
import pytest
from mixer.backend.django import mixer
from quizzes.models import SimpleQuiz

pytestmark = pytest.mark.django_db

import os


@pytest.fixture
def mixed_quiz():
    return mixer.blend(SimpleQuiz, content="lorem ipsum dolor")

def test_sanity(mixed_quiz):
    sq = SimpleQuiz.objects.get(content="lorem ipsum dolor")
    sq.content = "pig latin"
    sq.save()
    sq.refresh_from_db()
    assert sq.content == "pig latin"

def test_conftest_is_loading():
    assert os.environ['STRIPE_PUBLIC_KEY'] == '1234'



