from stripehandler.models import StripeSubscription
from users.models import User


"""
Product (test):
prod_PbUz9nyt8NAmEO  ---  read with abandon. need to make the real one of these.


"""


def handle_subscription_active(user: User, new_sub: StripeSubscription):
    """Handle a new user subscription or newly active subscription."""


def handle_subscription_deactivate(old_sub: StripeSubscription):
    """Handle subscription deleted."""
