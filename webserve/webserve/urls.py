from django.contrib import admin
from django.urls import path, include

from users.views import LandingPageView
from privateuploads.views import FileUploadView
from sharing.views import feedback_submit, ShareLandingRedirectView
from stripehandler.views import stripe_hook

from .api import api

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing_page"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("upload", FileUploadView.as_view(), name="upload_file"),
    path(
        "accounts/", include("django.contrib.auth.urls")
    ),  # Include the authentication URLs
    path("docs/", include("privateuploads.urls")),
    path("share/<str:guid>/", ShareLandingRedirectView.as_view(), name="share_landing"),
    path("share/feedback", feedback_submit, name="feedback_submit"),
    path("stripe_hook", stripe_hook, name="stripe_hook"),
]
