from django.urls import path
from . import views

urlpatterns = [
    path("list/rfp", views.RFPClusterListView.as_view(), name="rfp_list"),
    path("list/proposal", views.RFPClusterListView.as_view(), name="proposal_list"),
    path(
        "feedback/<str:guid>",
        views.DocumentClusterFeedbackView.as_view(),
        name="doc_cluster_feedback",
    ),
    path(
        "<int:pk>", views.DocumentClusterDetailView.as_view(), name="doc_cluster_detail"
    ),
    path(
        "<int:pk>/delete",
        views.DocumentClusterDeleteView.as_view(),
        name="doc_cluster_delete",
    ),
    path(
        "<int:pk>/reprocess",
        views.DocumentClusterReprocessView.as_view(),
        name="doc_cluster_reprocess",
    ),
    path(
        "<int:pk>/share",
        views.DocumentClusterCreateShareView.as_view(),
        name="doc_cluster_share",
    ),
    path("<int:pk>/raw", views.DocumentFileRawView.as_view(), name="doc_file_raw"),
    path(
        "<int:pk>/original",
        views.DocumentFileOriginalView.as_view(),
        name="doc_file_original",
    ),
]
