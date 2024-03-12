from datetime import date

from quizzes.history_compute import get_streak


def test_streak_starts_yesterday():
    today = date(2024, 2, 1)
    previous_dates = [date(2024, 1, 1), date(2024, 1, 31), date(2024, 1, 30)]
    assert 2 == get_streak(today, previous_dates)


def test_streak_starts_today():
    today = date(2024, 2, 1)
    previous_dates = [
        date(2024, 1, 1),
        date(2024, 1, 31),
        date(2024, 1, 30),
        date(2024, 2, 1),
    ]
    assert 3 == get_streak(today, previous_dates)


def test_empty_streak():
    today = date(2024, 2, 1)
    previous_dates = [
        date(2024, 1, 1),
        date(2024, 1, 30),
    ]
    assert 0 == get_streak(today, previous_dates)


def test_no_dates():
    today = date(2024, 1, 1)
    assert 0 == get_streak(today, [])
