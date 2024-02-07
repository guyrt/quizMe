import json
from ninja import Schema
from typing import List

from .models import SimpleQuiz


class MakeQuizIdSchemas(Schema):
    url_obj: int
    raw_doc: str
    force_recreate: bool = False


class SimpleQuizContentAnswerSchema(Schema):
    answer: str
    correct: int | None = None


class SimpleQuizContentSchema(Schema):
    question: str
    answers: List[SimpleQuizContentAnswerSchema]


class SimpleQuizSchema(Schema):
    was_created: bool = True
    owner: str
    content: List[SimpleQuizContentSchema]
    id: str
    reasoning: str
    status: str


class UploadQuizResultsSchema(Schema):
    quiz_id: str
    selection: List[int]


class QuizContextSchema(Schema):
    previous_quiz: SimpleQuizSchema
    latest_results: List[int]


class QuizStatsReturnSchema(Schema):
    total_quizzes: int
    quiz_allowance: int
    recent_quizzes: List[QuizContextSchema]


def create_simple_quiz_schema(obj: SimpleQuiz, was_created: bool) -> SimpleQuizSchema:
    try:
        content = json.loads(obj.content)
    except json.JSONDecodeError:
        content = []

    return SimpleQuizSchema(
        was_created=was_created,
        owner=str(obj.owner.pk),
        content=content,
        reasoning=obj.reasoning,
        id=str(obj.pk),
        status=obj.status,
    )
