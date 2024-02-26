from users.models import User


def customer_created(customer_id : str, customer_email : str):
    """Customer created handler - either match on email or log a failure."""
    if not customer_email:
        write_failure({'customer_id': customer_id, 'error': 'customer.create.noemail'})

    try:
        user = User.objects.get(email=customer_email)
    except User.DoesNotExist:
        write_failure({'customer_id': customer_id, 'error': 'customer.create.usernotfound'})
    else:
        # write a record
        pass


def write_failure(payload):
    pass
