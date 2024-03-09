from datetime import date, timedelta
from django.db.models.functions import TruncDay

from quizzes.models import SimpleQuiz

from typing import List


def history_aggregate(today, month_start):
    unique_days_count = list(
        SimpleQuiz.objects.filter(
            date_modified__date__gte=month_start
        )  # Filter quizzes modified in the current month
        .annotate(day=TruncDay("date_modified"))  # Truncate the date_modified to day
        .filter(
            simplequizresults__isnull=False
        )  # Ensure at least one result exists for the quiz
        .values("day")  # Group by the truncated day
        .distinct()
        .values_list("day")
    )

    return {
        "num_days_month": len(unique_days_count),
        "streak": get_streak(today, unique_days_count),
    }


def get_streak(today: date, dates: List[date]) -> int:
    dates.sort(reverse=True)
    current_streak = 1 if dates[0] == today else 0

    for i in range(1, len(dates)):
        # Check if the current date is consecutive with the previous date
        if dates[i] == dates[i - 1] - timedelta(days=1):
            current_streak += 1  # Increment current streak
        else:
            break

    return current_streak
