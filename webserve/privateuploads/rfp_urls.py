from django.urls import path
from . import views

urlpatterns = [
    path('list', views.RFPClusterListView.as_view(), name='doc_cluster_list'),
    path('<int:pk>', views.DocumentClusterDetailView.as_view(), name='doc_cluster_detail'),
    path('<int:pk>/delete', views.DocumentClusterDeleteView.as_view(), name='doc_cluster_delete'),
    path('<int:pk>/reprocess', views.DocumentClusterReprocessView.as_view(), name='doc_cluster_reprocess'),
]
