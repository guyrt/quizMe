from ninja import ModelSchema, Schema
from typing import List

from .models import SimpleQuiz


class MakeQuizIdSchemas(Schema):

    url_obj : int
    raw_doc : int
    force_recreate : bool = False


class SimpleQuizSchema(Schema):
    
    was_created : bool = True

    class Meta:
        model = SimpleQuiz
        fields = ['owner', 'content', 'id', 'reasoning']


class UploadQuizResultsSchema(Schema):

    quiz_id : str
    selection : List[int]
