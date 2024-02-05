import json
from dataclasses import dataclass
from django.db.models import OuterRef, Subquery

from extensionapis.models import RawDocCapture, SingleUrl
from quizzes.models import get_simple_quiz, SimpleQuizResults
from quizzes.schemas import SimpleQuizSchema, UploadQuizResultsSchema


@dataclass
class SingleUrlContext:

    quiz_obj : SimpleQuizSchema = None
    quiz_last_result : UploadQuizResultsSchema = None


def build_page_domain_history(single_url : SingleUrl):
    """Build a context object of history of page and of domain"""
    previous_visits_qs = RawDocCapture.objects.filter(active=1, url_model=single_url)
    num_previous_visits = previous_visits_qs.count()
    if num_previous_visits > 1:
        latest_visit = previous_visits_qs.order_by('-date_added')[1]
    else:
        latest_visit = None
    
    other_urls = SingleUrl.objects\
        .filter(user=single_url.user, active=1)\
        .exclude(id=single_url.pk)\
        .filter(host=single_url.host)\
        .order_by('-date_added')[:5]

    most_recent_capture = RawDocCapture.objects.filter(
        url_model=OuterRef('pk')
    ).order_by('-date_added')

    # We use a subquery to get the title of the most recent capture
    recent_capture_title = most_recent_capture.values('title')[:1]

    # Now, annotate the SingleUrl queryset
    single_urls_with_title = other_urls.annotate(
        recent_title=Subquery(recent_capture_title)
    )

    return {
        'recent_page_visits': {
            'number_visits': num_previous_visits,
            'latest_visit': latest_visit
        },
        'recent_domain_visits': single_urls_with_title
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
