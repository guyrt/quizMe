from django.urls import path
from . import views

urlpatterns = [
    path("list/urls", views.singleurl_list, name="singleurl_list"),
    path('singleurl/<uuid:guid>/', views.single_url_detail, name='singleurl_detail'),
    path('singleurl/<uuid:guid>/processcontenttemplates', views.process_content_template, name='process_content_templates')
]
