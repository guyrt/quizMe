import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from django.conf import settings

from .handlers import customer_created, customer_deleted

stripe.api_key = settings.STRIPE_SECRET_KEY


import logging
logger = logging.getLogger("default")

@csrf_exempt
@require_POST
def stripe_hook(request):

    body = json.loads(request.body)
    event_id = body['id']
    event_type = body['type']

    logger.info("Stripe event %s %s", event_id, event_type)
    if event_type == "customer.created":
        customer_id = body['data']['object']['id']
        customer_email = body.get('customer_email', '')
        customer_created(event_id, customer_id, customer_email)
    elif event_type == "customer.deleted":
        customer_id = body['data']['object']['id']
        customer_email = body.get('customer_email', '')
        customer_deleted(event_id, customer_id)
    elif event_type == "customer.subscription.created":
        # todo
        customer_email = body['customer_email']
        subscription = body['data']['object']['id']
    elif event_type == "customer.subscription.updated":
        # todo - figure out what the issue is. perhaps it's a cancel. you get a sub object.
        customer_id = body['data']['object']['customer']
        subscription = body['data']['object']['id']
    elif event_type == "customer.subscription.delete":
        # todo
        customer_id = body['data']['object']['id']
        customer_email = body.get('customer_email', '')
    elif event_type == "invoice.paid":
        # todo
        customer_email = body['customer_email']
        subscription = body['data']['object']['subscription']
    else:
        logger.info("Unhandled stripe event: %s %s", event_type, event_id)

    return HttpResponse(status=200)


# todo:
#   customer object - only one with get or create.
#   subscriptions object with 'state' that is active and inactive
#   events log
#   