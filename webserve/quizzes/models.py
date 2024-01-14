import uuid

from django.db import models
from users.models import User

from extensionapis.models import SingleUrl

from webserve.mixins import ModelBaseMixin

import logging
logger = logging.getLogger("default")


class SimpleQuiz(ModelBaseMixin):
    """Starter model - just stores a JSON blob."""

    class QuizStatus(models.TextChoices):
        NotStarted = "notstarted", "NotStarted"
        Building = "building", "Building"
        Completed = "completed", "Completed"
        Error = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    status = models.CharField(max_length=16, choices=QuizStatus, default=QuizStatus.NotStarted)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=10000)
    reasoning = models.TextField(max_length=10000)  # the natural language reasoning.

    url = models.ForeignKey(SingleUrl, on_delete=models.CASCADE)


class SimpleQuizResults(ModelBaseMixin):

    quiz = models.ForeignKey(SimpleQuiz, on_delete=models.CASCADE)
    
    # Stores results as a JSON list of ints.
    # -1 means no selection.
    results = models.TextField(max_length=64)


def get_simple_quiz(url_pk : str, user : User, create_if_not_exists, force_create=False) -> SimpleQuiz | None:
    if not force_create:
        try:
            existing_quiz = SimpleQuiz.objects.get(url__pk=url_pk, owner=user, active=1)
        except SimpleQuiz.MultipleObjectsReturned:
            existing_quiz = repair_quizzes(url_pk, user)
            logger.info("Returning existing quiz")
            return existing_quiz
        except SimpleQuiz.DoesNotExist:
            pass
        else:
            logger.info("Returning existing quiz")
            return existing_quiz

    if create_if_not_exists:
        return SimpleQuiz.objects.create(
            owner=user,
            content="[]",
            reasoning="",
            status=SimpleQuiz.QuizStatus.NotStarted,
            url_id=url_pk
        )
    else:
        return None


def repair_quizzes(url_pk : int, user : User):
    # repair if more than one quiz. Just keep latest.
    # not optimized - should be rare.
    all_quizzes = SimpleQuiz.objects.filter(url__pk=url_pk, owner=user, active=1)
    if len(all_quizzes) == 0:
        raise SimpleQuiz.DoesNotExist()
    all_quizzes = list(all_quizzes)
    old_quizzes = all_quizzes[:-1]
    for q in old_quizzes:
        logger.warn("Removing %s duplicate quizzes for url %s", len(old_quizzes), url_pk)
        q.active = False
        q.save()
    return all_quizzes[-1]
