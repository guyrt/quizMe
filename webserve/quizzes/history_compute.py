from datetime import date, timedelta

from quizzes.models import SimpleQuiz

from typing import Iterable, Set


def history_aggregate(user, today, month_start):
    unique_days = list(
        SimpleQuiz.objects.filter(
            owner=user, date_modified__date__gte=(today - timedelta(32))
        )  # Filter quizzes modified in the current month
        .filter(
            simplequizresults__isnull=False
        )  # Ensure at least one result exists for the quiz
        .values_list("date_modified")  # Group by the truncated day
    )

    simple_unique_days: Set[date] = set(u[0].date() for u in unique_days)

    month_start = today.replace(day=1)

    return {
        "num_days_month": len([s for s in simple_unique_days if s >= month_start]),
        "streak": get_streak(today, unique_days),
    }


def get_streak(today: date, dates: Iterable[date]) -> int:
    # needs testing
    # a streak can start with today or yesterday.
    if len(dates) == 0:
        return 0
    dates = list(dates)
    dates.sort(reverse=True)
    current_streak = 1 if dates[0] >= today - timedelta(days=1) else 0

    for i in range(1, len(dates)):
        # Check if the current date is consecutive with the previous date
        if dates[i] == dates[i - 1] - timedelta(days=1):
            current_streak += 1  # Increment current streak
        else:
            break

    return current_streak
