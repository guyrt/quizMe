from ninja import ModelSchema


from .models import SimpleQuiz


class SimpleQuizeSchema(ModelSchema):
    class Meta:
        model = SimpleQuiz
        fields = ['user', 'content', 'pk']
