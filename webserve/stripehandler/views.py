import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


import logging
logger = logging.getLogger("default")

@csrf_exempt
@require_POST
def stripe_hook(request):

    body = json.loads(request.body)
    event_id = body['id']
    event_type = body['type']

#    response = stripe.Event.retrieve(event_id)

    logger.info("Got event %s %s", event_id, event_type)
    if event_type == "customer.created":
        logger.info(body)
    elif event_type == "customer.subscription.created":
        sub_id = body['data']['object']['customer']
        sub = stripe.Customer.retrieve(sub_id)
        logger.info(sub)


#    logger.info(response)
    return HttpResponse(status=200)


"""
{
  "id": "evt_1OmPudGUMGPvycyBRpGtW9tg",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1708560798,
  "data": {
    "object": {
      "id": "in_1OmPuaGUMGPvycyBnD3Wk5KE",
      "object": "invoice",
      "account_country": "US",
      "account_name": "FlexIndex, Inc.",
      "account_tax_ids": null,
      "amount_due": 1500,
      "amount_paid": 1500,
      "amount_remaining": 0,
      "amount_shipping": 0,
      "application": null,
      "application_fee_amount": null,
      "attempt_count": 1,
      "attempted": true,
      "auto_advance": false,
      "automatic_tax": {
        "enabled": false,
        "liability": null,
        "status": null
      },
      "billing_reason": "subscription_create",
      "charge": "ch_3OmPuaGUMGPvycyB2t98abO8",
      "collection_method": "charge_automatically",
      "created": 1708560796,
      "currency": "usd",
      "custom_fields": null,
      "customer": "cus_PbdAY0s3Tog5Oz",
      "customer_address": null,
      "customer_email": null,
      "customer_name": null,
      "customer_phone": null,
      "customer_shipping": null,
      "customer_tax_exempt": "none",
      "customer_tax_ids": [

      ],
      "default_payment_method": null,
      "default_source": null,
      "default_tax_rates": [

      ],
      "description": null,
      "discount": null,
      "discounts": [

      ],
      "due_date": null,
      "effective_at": 1708560796,
      "ending_balance": 0,
      "footer": null,
      "from_invoice": null,
      "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1OAEPeGUMGPvycyB/test_YWNjdF8xT0FFUGVHVU1HUHZ5Y3lCLF9QYmRBVU9qSFdBdVhNTlA5Wm02ZExLam54VUtQQ2VzLDk5MTAxNTk50200ssqCK2vo?s=ap",
      "invoice_pdf": "https://pay.stripe.com/invoice/acct_1OAEPeGUMGPvycyB/test_YWNjdF8xT0FFUGVHVU1HUHZ5Y3lCLF9QYmRBVU9qSFdBdVhNTlA5Wm02ZExLam54VUtQQ2VzLDk5MTAxNTk50200ssqCK2vo/pdf?s=ap",
      "issuer": {
        "type": "self"
      },
      "last_finalization_error": null,
      "latest_revision": null,
      "lines": {
        "object": "list",
        "data": [
          {
            "id": "il_1OmPuaGUMGPvycyBTp3TLY5O",
            "object": "line_item",
            "amount": 1500,
            "amount_excluding_tax": 1500,
            "currency": "usd",
            "description": "1 \xc3\x97 myproduct (at $15.00 / month)",
            "discount_amounts": [

            ],
            "discountable": true,
            "discounts": [

            ],
            "invoice": "in_1OmPuaGUMGPvycyBnD3Wk5KE",
            "livemode": false,
            "metadata": {
            },
            "period": {
              "end": 1711066396,
              "start": 1708560796
            },
            "plan": {
              "id": "price_1OmPuaGUMGPvycyBKnmqg7QT",
              "object": "plan",
              "active": true,
              "aggregate_usage": null,
              "amount": 1500,
              "amount_decimal": "1500",
              "billing_scheme": "per_unit",
              "created": 1708560796,
              "currency": "usd",
              "interval": "month",
              "interval_count": 1,
              "livemode": false,
              "metadata": {
              },
              "nickname": null,
              "product": "prod_PbdAItdzGTG5mw",
              "tiers_mode": null,
              "transform_usage": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "price": {
              "id": "price_1OmPuaGUMGPvycyBKnmqg7QT",
              "object": "price",
              "active": true,
              "billing_scheme": "per_unit",
              "created": 1708560796,
              "currency": "usd",
              "custom_unit_amount": null,
              "livemode": false,
              "lookup_key": null,
              "metadata": {
              },
              "nickname": null,
              "product": "prod_PbdAItdzGTG5mw",
              "recurring": {
                "aggregate_usage": null,
                "interval": "month",
                "interval_count": 1,
                "trial_period_days": null,
                "usage_type": "licensed"
              },
              "tax_behavior": "unspecified",
              "tiers_mode": null,
              "transform_quantity": null,
              "type": "recurring",
              "unit_amount": 1500,
              "unit_amount_decimal": "1500"
            },
            "proration": false,
            "proration_details": {
              "credited_items": null
            },
            "quantity": 1,
            "subscription": "sub_1OmPuaGUMGPvycyBbRu736Yb",
            "subscription_item": "si_PbdAitKlHaXY0j",
            "tax_amounts": [

            ],
            "tax_rates": [

            ],
            "type": "subscription",
            "unit_amount_excluding_tax": "1500"
          }
        ],
        "has_more": false,
        "total_count": 1,
        "url": "/v1/invoices/in_1OmPuaGUMGPvycyBnD3Wk5KE/lines"
      },
      "livemode": false,
      "metadata": {
      },
      "next_payment_attempt": null,
      "number": "016956F6-0001",
      "on_behalf_of": null,
      "paid": true,
      "paid_out_of_band": false,
      "payment_intent": "pi_3OmPuaGUMGPvycyB2MEogm9W",
      "payment_settings": {
        "default_mandate": null,
        "payment_method_options": null,
        "payment_method_types": null
      },
      "period_end": 1708560796,
      "period_start": 1708560796,
      "post_payment_credit_notes_amount": 0,
      "pre_payment_credit_notes_amount": 0,
      "quote": null,
      "receipt_number": null,
      "rendering": null,
      "rendering_options": null,
      "shipping_cost": null,
      "shipping_details": null,
      "starting_balance": 0,
      "statement_descriptor": null,
      "status": "paid",
      "status_transitions": {
        "finalized_at": 1708560796,
        "marked_uncollectible_at": null,
        "paid_at": 1708560796,
        "voided_at": null
      },
      "subscription": "sub_1OmPuaGUMGPvycyBbRu736Yb",
      "subscription_details": {
        "metadata": {
        }
      },
      "subtotal": 1500,
      "subtotal_excluding_tax": 1500,
      "tax": null,
      "test_clock": null,
      "total": 1500,
      "total_discount_amounts": [

      ],
      "total_excluding_tax": 1500,
      "total_tax_amounts": [

      ],
      "transfer_data": null,
      "webhooks_delivered_at": null
    }
  },
  "livemode": false,
  "pending_webhooks": 2,
  "request": {
    "id": "req_4Ld5mKGJZM5p62",
    "idempotency_key": "4f16b29d-b167-42b9-8390-73a920f2c5f8"
  },
  "type": "invoice.payment_succeeded"
}
"""