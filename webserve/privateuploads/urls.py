from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.FileUploadView.as_view(), name='upload_rfp'),
    path('list', views.DocumentClusterListView.as_view(), name='doc_cluster_list'),
    path('rfp/<int:id>', views.DocumentClusterDetailView.as_view(), name='doc_cluster_detail')
]
