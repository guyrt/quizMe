from json import dumps
import logging
import time

from django.shortcuts import get_object_or_404
from users.apiauth import ApiKey
from extensionapis.models import RawDocCapture
from ninja import Router
from ninja.errors import HttpError

from .models import SimpleQuiz, repair_quizzes, SimpleQuizResults
from .quiz_gen import QuizGenerator
from .schemas import MakeQuizIdSchemas, SimpleQuizSchema, UploadQuizResultsSchema

logger = logging.getLogger("default")

router = Router(auth=ApiKey(), tags=['quizzes'])


@router.post("makequiz", response=SimpleQuizSchema)
def make_quiz(request, body : MakeQuizIdSchemas):
    """
    If a quiz exists for this URL, return it. (Maybe later have a force recreate as a sign it's bad.)
    """
    user = request.auth
    logger.info("Write quiz for %s for user %s", body.url_obj, user.pk)
    
    if body.force_recreate:
        pass
    else:
        try:
            existing_quiz = SimpleQuiz.objects.get(url__pk=body.url_obj, owner=user, active=1)
        except SimpleQuiz.MultipleObjectsReturned:
            existing_quiz = repair_quizzes(body.url_obj, user)
            logger.info("Returning existing quiz")
            return _create_model_schema(existing_quiz, was_created=False)
        except SimpleQuiz.DoesNotExist:
            pass
        else:
            logger.info("Returning existing quiz")
            return _create_model_schema(existing_quiz, was_created=False)

    qs = RawDocCapture.objects.select_related("url_model").prefetch_related("url_model__singleurlfact_set")
    raw_doc = get_object_or_404(qs, id=body.raw_doc, user=user, active=1)

    # try to get an extract.
    # if none (there won't be one now) then assume someone is making one. don't wait.
    #     just extract from DOM and send to the quiz gen logic.
    # quiz gen is simple prompt + store PromptResponse + return content in JSON format.
    start_time = time.time()
    quiz = QuizGenerator().create_quiz(raw_doc)
    total_time = time.time() - start_time
    if quiz:
        logger.info("Quiz built in %s", total_time)
        return _create_model_schema(quiz, True)

    logger.info("Quiz did not build in %s seconds", total_time)
    
    raise HttpError(424, "{}")


def _create_model_schema(obj : SimpleQuiz, was_created : bool) -> SimpleQuizSchema:
    return SimpleQuizSchema(
        was_created=was_created,
        owner=str(obj.owner.pk),
        content=obj.content,
        reasoning=obj.reasoning,
        id=str(obj.pk)
    )


@router.post("uploadresults")
def upload_quiz(request, body : UploadQuizResultsSchema):
    
    sq = get_object_or_404(SimpleQuiz, id=body.quiz_id, owner=request.auth)
        
    SimpleQuizResults.objects.create(
        quiz=sq,
        results=dumps(body.selection)
    )

    return {}
