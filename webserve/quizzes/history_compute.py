from datetime import date, timedelta, datetime

from quizzes.models import SimpleQuiz
from typing import Iterable, Set

from users.models import User


def history_aggregate(user: User, today: datetime):
    unique_days = list(
        SimpleQuiz.objects.filter(
            owner=user, date_modified__gte=(today - timedelta(32))
        )  # Filter quizzes modified in the current month
        .filter(
            simplequizresults__isnull=False
        )  # Ensure at least one result exists for the quiz
        .values_list("date_modified", flat=True)  # Group by the truncated day
    )

    simple_unique_days: Set[date] = set([s.date() for s in unique_days])

    month_start = today.replace(day=1).date()

    return {
        "num_days_month": len([s for s in simple_unique_days if s >= month_start]),
        "streak": get_streak(today, simple_unique_days),
    }


def get_streak(today: datetime, dates: Iterable[datetime]) -> int:
    # needs testing
    # a streak can start with today or yesterday.
    if len(dates) == 0:
        return 0
    today = today.date()
    dates = list(dates)
    dates.sort(reverse=True)
    dates.insert(0, today)
    current_streak = 0

    for i in range(1, len(dates)):
        # Check if the current date is consecutive with the previous date
        if dates[i] >= dates[i - 1] - timedelta(
            days=1
        ):  # >= to support equal at start.
            current_streak += 1  # Increment current streak
        else:
            break

    return current_streak
