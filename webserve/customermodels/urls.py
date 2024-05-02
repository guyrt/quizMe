from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:pk>", views.show_schema, name="schema_details"),
    path("create", views.create_dataschema, name="schema_create"),

    path('singleurl/<uuid:guid>/processcontenttemplates', views.process_content_template, name='process_content_templates'),
    path('singleurl/<uuid:guid>/extractions', views.show_extractions, name='show_content_extract')
]
