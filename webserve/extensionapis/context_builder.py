from dataclasses import dataclass

from extensionapis.models import SingleUrl
from quizzes.models import get_simple_quiz, SimpleQuizResults
from quizzes.schemas import SimpleQuizSchema, UploadQuizResultsSchema


@dataclass
class SingleUrlContext:

    quiz_obj : SimpleQuizSchema = None
    quiz_last_result : UploadQuizResultsSchema = None


def build_context(single_url : SingleUrl) -> SingleUrlContext:
    """Build context needed by the extension Front End to help maintain the FSM for reentry."""
    quiz = get_simple_quiz(single_url.pk, single_url.user)
    ret = SingleUrlContext(quiz_obj=quiz)
    if quiz is not None:
        latest_results = SimpleQuizResults.objects.filter(quiz=quiz, active=1).latest('date_added')
        if latest_results:
            ret.quiz_last_result = latest_results
    return ret
