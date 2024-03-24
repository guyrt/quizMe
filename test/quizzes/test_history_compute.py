import pytest
from datetime import date
from django.utils import timezone

from mixer.backend.django import mixer
from quizzes.models import SimpleQuiz, SimpleQuizResults

from quizzes.history_compute import get_streak, history_aggregate
from ..users.fixtures import existing_user  # noqa


pytestmark = pytest.mark.django_db


@pytest.fixture
def build_quiz_history(existing_user):  # noqa
    """
    dummy example. mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    date_modified_field = SimpleQuiz._meta.get_field("date_modified")
    # Temporarily disable auto_now
    auto_now_original = date_modified_field.auto_now
    date_modified_field.auto_now = False

    sq_1 = mixer.blend(
        SimpleQuiz,
        owner=existing_user,
        content="lorem ipsum dolor",
        date_modified=timezone.datetime(2024, 1, 10, 12, 1, 0),
    )
    sq_2 = mixer.blend(
        SimpleQuiz,
        owner=existing_user,
        content="lorem ipsum dolor2",
        date_modified=timezone.datetime(2024, 1, 20, 12, 1, 0),
    )
    sq_3 = mixer.blend(
        SimpleQuiz,
        owner=existing_user,
        content="lorem ipsum dolor2",
        date_modified=timezone.datetime(2024, 2, 1, 12, 1, 0),
    )
    sq_4 = mixer.blend(
        SimpleQuiz,
        owner=existing_user,
        content="lorem ipsum dolor2",
        date_modified=timezone.datetime(2024, 2, 1, 13, 1, 0),
    )

    mixer.blend(SimpleQuizResults, quiz=sq_1, results="[1]")
    mixer.blend(SimpleQuizResults, quiz=sq_2, results="[2]")
    mixer.blend(SimpleQuizResults, quiz=sq_3, results="[3]")
    mixer.blend(SimpleQuizResults, quiz=sq_4, results="[-1]")

    try:
        yield (sq_1, sq_2, sq_3, sq_4)
    finally:
        date_modified_field.auto_now = auto_now_original


def test_e2e_quiz_history(existing_user, build_quiz_history):  # noqa
    assert 4 == SimpleQuiz.objects.count()
    today = timezone.datetime(2024, 2, 2)  # this should catch sq_2, sq_3 but not sq_1
    payload = history_aggregate(existing_user, today)

    assert payload["num_days_month"] == 1
    assert payload["streak"] == 1


def test_e2e_quiz_history_no_streak(existing_user, build_quiz_history):  # noqa
    assert 4 == SimpleQuiz.objects.count()
    today = timezone.datetime(2024, 2, 3)
    payload = history_aggregate(existing_user, today)

    assert payload["num_days_month"] == 1
    assert payload["streak"] == 0


def test_streak_starts_yesterday():
    today = timezone.datetime(2024, 2, 1)
    previous_dates = [date(2024, 1, 1), date(2024, 1, 31), date(2024, 1, 30)]
    assert 2 == get_streak(today, previous_dates)


def test_streak_starts_today():
    today = timezone.datetime(2024, 2, 1)
    previous_dates = [
        date(2024, 1, 1),
        date(2024, 1, 31),
        date(2024, 1, 30),
        date(2024, 2, 1),
    ]
    assert 3 == get_streak(today, previous_dates)


# regression
def test_consecutive_with_break():
    today = timezone.datetime(2024, 3, 23)
    previous_dates = [date(2024, 3, 15), date(2024, 3, 16)]
    assert 0 == get_streak(today, previous_dates)


def test_empty_streak():
    today = timezone.datetime(2024, 2, 1)
    previous_dates = [
        date(2024, 1, 1),
        date(2024, 1, 30),
    ]
    assert 0 == get_streak(today, previous_dates)


def test_no_dates():
    today = timezone.datetime(2024, 1, 1)
    assert 0 == get_streak(today, [])
