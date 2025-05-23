from json import dumps
import logging
import time

from django.shortcuts import get_object_or_404

from django.utils import timezone
from quizzes.history_compute import history_aggregate
from stripehandler.business_logic import get_redirect
from users.apiauth import ApiKey
from users.models import get_active_subscription

from extensionapis.models import RawDocCapture
from extensionapis.schemas import WriteDomReturnSchema
from ninja import Router
from ninja.errors import HttpError


from .models import SimpleQuiz, SimpleQuizResults, get_simple_quiz
from .quiz_gen import QuizGenerator
from .schemas import (
    create_simple_quiz_schema,
    MakeQuizIdSchemas,
    QuizStatsReturnSchema,
    UploadQuizResultsSchema,
)

logger = logging.getLogger("default")

router = Router(auth=ApiKey(), tags=["quizzes"])


@router.get("stats", response=QuizStatsReturnSchema)
def quiz_stats(request):
    """
    Return all statistics that we know about quizzes.

    - num quizzes created
    - all quizzes Created this month

    This is used to gate access, so should include billing info.
    """
    user = request.auth

    quiz_q = SimpleQuiz.objects.filter(
        owner=user,
        active=True,
        status__in=[SimpleQuiz.QuizStatus.Completed, SimpleQuiz.QuizStatus.Building],
    )
    total_quizzes = quiz_q.count()
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0)

    recent_quizzes = quiz_q.filter(date_added__gte=month_start).prefetch_related(
        "simplequizresults_set"
    )

    quiz_allowance = get_active_subscription(user).quiz_allowance

    quiz_contexts = [create_simple_quiz_schema(q, False) for q in recent_quizzes]

    stats = history_aggregate(user, today)
    stats.update(
        {
            "total_quizzes": total_quizzes,
            "recent_quizzes": quiz_contexts,
            "quiz_allowance": quiz_allowance,
            "stripe_redirect": get_redirect(user),
        }
    )

    return stats


@router.post("makequiz", response=WriteDomReturnSchema)
def make_quiz(request, body: MakeQuizIdSchemas):
    """
    If a quiz exists for this URL, return it.
    """

    user = request.auth
    logger.info("Write quiz for %s for user %s", body.url_obj, user.pk)

    quiz = get_simple_quiz(body.url_obj, user, True, body.force_recreate)
    if quiz.status != SimpleQuiz.QuizStatus.NotStarted:
        # note that we return Error quizzes too. This should trigger "recreate" on the FE.
        return _make_quiz_return_object(body, quiz, False)

    qs = RawDocCapture.objects.select_related("url_model").prefetch_related(
        "url_model__singleurlfact_set"
    )
    raw_doc = get_object_or_404(qs, pk=body.raw_doc, user=user, active=1)

    # try to get an extract.
    # if none (there won't be one now) then assume someone is making one. don't wait.
    #     just extract from DOM and send to the quiz gen logic.
    # quiz gen is simple prompt + store PromptResponse + return content in JSON format.
    start_time = time.time()
    quiz = QuizGenerator().create_quiz(raw_doc, quiz.id)
    total_time = time.time() - start_time
    if quiz:
        logger.info("Quiz built in %s", total_time)
        return _make_quiz_return_object(body, quiz, True)

    logger.info("Quiz did not build in %s seconds", total_time)

    raise HttpError(424, "{}")


def _make_quiz_return_object(
    body: MakeQuizIdSchemas, quiz: SimpleQuiz, was_created: bool
) -> WriteDomReturnSchema:
    return WriteDomReturnSchema.model_validate(
        {
            "raw_doc": body.raw_doc,
            "url_obj": body.url_obj,
            "quiz_context": create_simple_quiz_schema(quiz, was_created),
        }
    )


@router.post("uploadresults")
def upload_quiz(request, body: UploadQuizResultsSchema):
    sq = get_object_or_404(SimpleQuiz, id=body.quiz_id, owner=request.auth)

    SimpleQuizResults.objects.create(quiz=sq, results=dumps(body.selection))

    return quiz_stats(request)
