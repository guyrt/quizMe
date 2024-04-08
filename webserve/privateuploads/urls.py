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
        "<uuid:pk>",
        views.DocumentClusterDetailView.as_view(),
        name="doc_cluster_detail",
    ),
    path(
        "<uuid:pk>/delete",
        views.DocumentClusterDeleteView.as_view(),
        name="doc_cluster_delete",
    ),
    path(
        "<uuid:pk>/reprocess",
        views.DocumentClusterReprocessView.as_view(),
        name="doc_cluster_reprocess",
    ),
    path(
        "<uuid:pk>/share",
        views.DocumentClusterCreateShareView.as_view(),
        name="doc_cluster_share",
    ),
    path("<uuid:pk>/raw", views.DocumentFileRawView.as_view(), name="doc_file_raw"),
    path(
        "<uuid:pk>/original",
        views.DocumentFileOriginalView.as_view(),
        name="doc_file_original",
    ),
]
