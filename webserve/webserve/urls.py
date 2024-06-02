from django.urls import path, include

from users.views import LandingPageView, PrivacyPage
from stripehandler.views import stripe_hook

from .api import api

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing_page"),
    path("privacy", PrivacyPage.as_view(), name="privacy"),
    path("api/", api.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("web/", include("extensionapis.urls")),
    path("stripe_hook", stripe_hook, name="stripe_hook"),
]
