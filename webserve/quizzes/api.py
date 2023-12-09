from json import loads
from urllib import response
from django.shortcuts import get_object_or_404
from ninja import Router
import logging

from extensionapis.auth import ApiKey
from extensionapis.models import RawDocCapture
from .models import SimpleQuiz
from .schemas import SimpleQuizeSchema, MakeQuizIdSchemas
from .quiz_gen import QuizGenerator

logger = logging.getLogger("webstack")

router = Router(auth=ApiKey())


@router.post("makequiz", response=SimpleQuizeSchema | str)
def make_quiz(request, body : MakeQuizIdSchemas):
    """
    If a quiz exists for this URL, return it. (Maybe later have a force recreate as a sign it's bad.)
    """
    user = request.auth

    try:
        existing_quiz = SimpleQuiz.objects.get(url__pk=body.url_obj, owner=user, active=1)
    except SimpleQuiz.DoesNotExist:
        pass
    else:
        return SimpleQuizeSchema(existing_quiz)

    raw_doc = get_object_or_404(RawDocCapture, id=body.raw_doc, user=user, active=1)

    # try to get an extract.
    # if none (there won't be one now) then assume someone is making one. don't wait.
    #     just extract from DOM and send to the quiz gen logic.
    # quiz gen is simple prompt + store PromptResponse + return content in JSON format.
    quiz = QuizGenerator().create_quiz(raw_doc)
    if quiz:
        return SimpleQuizeSchema(quiz)
    return ""