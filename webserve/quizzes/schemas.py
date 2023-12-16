from ninja import ModelSchema, Schema
from typing import List

from .models import SimpleQuiz


class MakeQuizIdSchemas(Schema):

    url_obj : int
    raw_doc : int


class SimpleQuizSchema(ModelSchema):
    class Meta:
        model = SimpleQuiz
        fields = ['owner', 'content', 'id', 'reasoning']


class UploadQuizResultsSchema(Schema):

    quiz_id : int
    selection : List[int]
