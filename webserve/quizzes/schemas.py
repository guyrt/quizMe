from ninja import ModelSchema, Schema


from .models import SimpleQuiz


class MakeQuizIdSchemas(Schema):

    url_obj : int
    raw_doc : int


class SimpleQuizSchema(ModelSchema):
    class Meta:
        model = SimpleQuiz
        fields = ['owner', 'content', 'id', 'reasoning']
