from json import loads
from django.shortcuts import get_object_or_404
from ninja import Router
import logging

from extensionapis.auth import ApiKey
from extensionapis.models import SingleUrl
from .models import SimpleQuiz
from .schemas import SimpleQuizeSchema

logger = logging.getLogger("webstack")

router = Router(auth=ApiKey())


@router.post("makequiz")
def make_quiz(request):
    """
    If a quiz exists for this URL, return it. (Maybe later have a force recreate as a sign it's bad.)
    """
    body = loads(request.body)
    user = request.auth

    try:
        existing_quiz = SimpleQuiz.objects.get(id=body['url_obj'], owner=user, active=1)
    except SimpleQuiz.DoesNotExist:
        pass
    else:
        return SimpleQuizeSchema(existing_quiz)

    url_obj = get_object_or_404(SingleUrl, id=body['url_obj'])

    # try to get an extract.
    # if none (there won't be one now) then assume someone is making one. don't wait.
    #     just extract from DOM and send to the quiz gen logic.
    # quiz gen is simple prompt + store PromptResponse + return content in JSON format.
