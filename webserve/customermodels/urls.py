from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:pk>", views.show_schema, name="schema_details"),
    path("create", views.create_dataschema, name="schema_create"),
]
