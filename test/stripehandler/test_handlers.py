import pytest
from users.models import User
from mixer.backend.django import mixer

from stripehandler.handlers import customer_created, customer_deleted
from stripehandler.models import StripeErrorLog, StripeUser

pytestmark = pytest.mark.django_db


@pytest.fixture
def existing_user():
    """
    Dummy example. Mixer auto-populates any object attributes that
    we don't manually override with kwargs, then creates the object.
    """
    return mixer.blend(User, email="exists@user.com")


@pytest.fixture
def existing_stripe_user(existing_user):
    return mixer.blend(StripeUser, id="earlierEvent", user=existing_user)


def test_add_to_user(existing_user):
    customer_created("event1", "newcustomerid1", "exists@user.com")

    su = StripeUser.objects.get(user=existing_user)
    assert su.id == "newcustomerid1"


def test_add_to_user_no_email(existing_user):
    customer_created("event2", "newcustomerid", "")

    error = StripeErrorLog.objects.get(event_id="event2")
    assert 'customer.create.noemail' in error.message

    assert 0 == StripeUser.objects.filter(user=existing_user).count()


def test_add_to_user_no_match(existing_user):
    customer_created("event3", "newcustomerid", "mismatch@user.com")

    error = StripeErrorLog.objects.get(event_id="event3")
    assert 'customer.create.usernotfound' in error.message

    assert 0 == StripeUser.objects.filter(user=existing_user).count()


def test_add_to_user_existing(existing_user, existing_stripe_user):
    customer_created("event4", "newcustomerid", "exists@user.com")

    error = StripeErrorLog.objects.get(event_id="event4")
    assert 'customer.create.duplicateStripeUser' in error.message

    su = StripeUser.objects.get(user=existing_user)
    assert su.id == existing_stripe_user.pk


def test_delete_user_exists(existing_stripe_user):
    customer_deleted("eventNew", existing_stripe_user.id)
    assert 0 == StripeUser.objects.filter(pk=existing_stripe_user.pk).count()


def test_delete_user_not_exists(existing_stripe_user):
    customer_deleted("eventNew", existing_stripe_user.id + "fail")
    
    # didn't drop what exists
    assert 1 == StripeUser.objects.filter(pk=existing_stripe_user.pk).count()

    error = StripeErrorLog.objects.get(event_id="eventNew")
    assert 'customer.delete.stripeusernotfound' in error.message
