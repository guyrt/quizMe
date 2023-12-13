import logging
import time

from django.shortcuts import get_object_or_404
from extensionapis.auth import ApiKey
from extensionapis.models import RawDocCapture
from ninja import Router
from ninja.errors import HttpError

from .models import SimpleQuiz
from .quiz_gen import QuizGenerator
from .schemas import MakeQuizIdSchemas, SimpleQuizSchema

logger = logging.getLogger("default")

router = Router(auth=ApiKey())


@router.post("makequiz", response=SimpleQuizSchema)
def make_quiz(request, body : MakeQuizIdSchemas):
    """
    If a quiz exists for this URL, return it. (Maybe later have a force recreate as a sign it's bad.)
    """
    user = request.auth
    logger.info("Write quiz for %s for user %s", body.url_obj, user.pk)

    try:
        existing_quiz = SimpleQuiz.objects.get(url__pk=body.url_obj, owner=user, active=1)
    except SimpleQuiz.DoesNotExist:
        pass
    else:
        logger.info("Returning existing quiz")
        return existing_quiz

    raw_doc = get_object_or_404(RawDocCapture, id=body.raw_doc, user=user, active=1)

    # try to get an extract.
    # if none (there won't be one now) then assume someone is making one. don't wait.
    #     just extract from DOM and send to the quiz gen logic.
    # quiz gen is simple prompt + store PromptResponse + return content in JSON format.
    start_time = time.time()
    quiz = QuizGenerator().create_quiz(raw_doc)
    total_time = time.time() - start_time
    if quiz:
        logger.info("Quiz built in %s", total_time)
        return quiz

    logger.info("Quiz did not build in %s seconds", total_time)
    
    raise HttpError(424, "{}")
