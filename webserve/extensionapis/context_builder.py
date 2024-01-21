import json
from dataclasses import dataclass

from extensionapis.models import RawDocCapture, SingleUrl
from quizzes.models import get_simple_quiz, SimpleQuizResults
from quizzes.schemas import SimpleQuizSchema, UploadQuizResultsSchema


@dataclass
class SingleUrlContext:

    quiz_obj : SimpleQuizSchema = None
    quiz_last_result : UploadQuizResultsSchema = None


def build_page_domain_history(single_url : SingleUrl):
    """Build a context object of history of page and of domain"""
    previous_visits = RawDocCapture.objects.filter(active=1, url_model=single_url).order_by('-date_added')[:5]
    other_urls = SingleUrl.objects\
        .filter(user=single_url.user, active=1)\
        .exclude(id=single_url.pk)\
        .filter(host=single_url.host)\
        .order_by('-date_added')[:5]

    return {
        'recent_page_visits': previous_visits,
        'recent_domain_visits': other_urls
    }


def build_quiz_context(single_url : SingleUrl) -> SingleUrlContext:
    """Build context needed by the extension Front End to help maintain the FSM for reentry."""
    quiz = get_simple_quiz(single_url.pk, single_url.user, create_if_not_exists=False)

    if not quiz:
        return None
    sqs = SimpleQuizSchema(
        was_created=False,
        owner=str(quiz.owner_id),
        content=json.loads(quiz.content),
        id=str(quiz.pk),
        reasoning=quiz.reasoning,
        status=quiz.status
    )
    ret = SingleUrlContext(quiz_obj=sqs, quiz_last_result=[])
    if quiz is not None:
        try:
            latest_results = SimpleQuizResults.objects.filter(quiz=quiz, active=1).latest('date_added')
            ret.quiz_last_result = json.loads(latest_results.results)
        except SimpleQuizResults.DoesNotExist:
            pass
    return ret
