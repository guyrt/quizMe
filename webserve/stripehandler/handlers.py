import json

from django.db import IntegrityError

from stripehandler.models import StripeUser, StripeErrorLog
from users.models import User

import logging
logger = logging.getLogger("default")


def customer_created(event_id : str, customer_id : str, customer_email : str):
    """Customer created handler - either match on email or log a failure.
    """
    if not customer_email:
        write_failure(event_id, {'customer_id': customer_id, 'error': 'customer.create.noemail'})
        return

    try:
        user = User.objects.get(email=customer_email)
    except User.DoesNotExist:
        write_failure(event_id, {'customer_id': customer_id, 'error': 'customer.create.usernotfound'})
        return

    # Write the record
    try:
        StripeUser.objects.get_or_create(
            user=user,
            id=customer_id
        )
    except IntegrityError:
        write_failure(event_id, {'customer_id': customer_id, 'error': 'customer.create.duplicateStripeUser'})


def customer_deleted(event_id : str, customer_id : str):
    
    try:
        su = StripeUser.objects.get(id=customer_id)
    except StripeUser.DoesNotExist:
        write_failure(event_id, {'customer_id': customer_id, 'error': 'customer.delete.stripeusernotfound'})
        return

    # Write the record
    su.delete()


def write_failure(event_id, payload):
    payload_s = json.dumps(payload)
    logger.error("Stripe error on %s: %s", event_id, payload_s)
    StripeErrorLog.objects.create(message=payload_s, event_id=event_id)
