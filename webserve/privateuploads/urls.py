from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.FileUploadView.as_view(), name='upload_rfp'),
]
