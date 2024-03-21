from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from django.utils import timezone
import uuid
from users.settings_logic import populate_default_settings

from webserve.mixins import ModelBaseMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        self.create_subscription(user)
        populate_default_settings(user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def create_subscription(self, user):
        return UserSubscriptions.objects.create(
            user=user, subscription=UserSubscriptions.SubscriptionTypes.Free
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserKeys(ModelBaseMixin):
    """Encryption key manager."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Name of an encyrption key in Azure Key Vault.
    name = models.CharField(max_length=128)


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    key = models.CharField(max_length=128)

    name = models.CharField(max_length=64)


class UserSubscriptions(ModelBaseMixin):
    class SubscriptionTypes(models.TextChoices):
        Free = "free", "free"
        MonthlyQuiz = "monthly_quiz", "monthly_quiz"

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subscription = models.CharField(max_length=32, choices=SubscriptionTypes)

    quiz_allowance = models.IntegerField(
        default=5
    )  # number of quizzes allowed per month. # 5 is free.


class LooseUserSettings(ModelBaseMixin):
    """Intended as a basic key/value store. We make no assumptions on uniqueness of keys.

    E.G. Canonical use case is to save exclusion domains. You can do this by saving
    key = 'domain.exclude'
    value = 'www.google.com'

    Specific keys are up to implementor.
    """

    class KnownKeys:
        DomainExclude = "domain.exclude"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=256)


def get_active_subscription(user) -> UserSubscriptions:
    """Get the best active subscription"""
    subs = UserSubscriptions.objects.filter(user=user, active=True)
    if len(subs) == 0:
        return UserSubscriptions.objects.create(
            user=user, subscription=UserSubscriptions.SubscriptionTypes.Free
        )

    for ranked_type in ["annual_quiz", "monthly_quiz", "free"]:
        for s in subs:
            if s.subscription == ranked_type:
                return s

    raise ValueError(
        f"Couldn't find known subscription type. User has sub {subs[0].subscription}"
    )
