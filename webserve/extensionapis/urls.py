from django.urls import path
from . import views

urlpatterns = [
    path("list/urls", views.singleurl_list, name="singleurl_list"),
]
