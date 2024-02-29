import json

from django.db import IntegrityError
from stripehandler.business_logic import (
    handle_subscription_active,
    handle_subscription_deactivate,
)

from stripehandler.models import StripeSubscription, StripeUser, StripeErrorLog
from users.models import User

import logging

logger = logging.getLogger("default")


def customer_created(event_id: str, customer_id: str, customer_email: str):
    """Customer created handler - either match on email or log a failure."""
    if not customer_email:
        write_failure(
            event_id, {"customer_id": customer_id, "error": "customer.create.noemail"}
        )
        return

    try:
        user = User.objects.get(email=customer_email)
    except User.DoesNotExist:
        write_failure(
            event_id,
            {"customer_id": customer_id, "error": "customer.create.usernotfound"},
        )
        return

    # Write the record
    try:
        StripeUser.objects.get_or_create(user=user, id=customer_id)
    except IntegrityError:
        write_failure(
            event_id,
            {
                "customer_id": customer_id,
                "error": "customer.create.duplicateStripeUser",
            },
        )


def customer_deleted(event_id: str, customer_id: str):
    try:
        su = StripeUser.objects.get(id=customer_id)
    except StripeUser.DoesNotExist:
        write_failure(
            event_id,
            {"customer_id": customer_id, "error": "customer.delete.stripeusernotfound"},
        )
        return

    # Write the record
    su.delete()


def subscription_created(event_id: str, customer_id: str, subscription_id: str):
    """Ensure objects are correctly created, create subscription, and update business logic."""
    try:
        su = StripeUser.objects.get(id=customer_id)
    except StripeUser.DoesNotExist:
        write_failure(
            event_id,
            {
                "subscription_id": subscription_id,
                "customer_id": customer_id,
                "error": "subscription.create.stripeusernotfound",
            },
        )
        return

    new_sub, created = StripeSubscription.objects.get_or_create(
        id=subscription_id, stripe_user=su
    )
    if created and new_sub.active is False:
        new_sub.active = True
        new_sub.save()

    handle_subscription_active(su.user, new_sub)


def subscription_updated(
    event_id: str, customer_id: str, subscription_id: str, subscription_payload
):
    """Tricky tricky... many options here. For now write failure."""
    write_failure(
        event_id,
        {
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "error": "subscription.create.stripeusernotfound",
        },
    )


def subscription_deleted(event_id: str, subscription: str):
    try:
        su = StripeSubscription.objects.get(id=subscription)
    except StripeSubscription.DoesNotExist:
        write_failure(
            event_id,
            {
                "subscription_id": subscription,
                "error": "subscription.delete.stripesubscriptionnotfound",
            },
        )
        return

    # Write the record
    su.active = False
    su.save()

    handle_subscription_deactivate(su)


def write_failure(event_id, payload):
    payload_s = json.dumps(payload)
    logger.error("Stripe error on %s: %s", event_id, payload_s)
    StripeErrorLog.objects.create(message=payload_s, event_id=event_id)
