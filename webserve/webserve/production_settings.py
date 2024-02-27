from .shared_settings import *

DEBUG = False

ALLOWED_HOSTS = ['.azurecontainerapps.io', 'wezo.ai'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://*.azurecontainerapps.io'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

# SECURITY WARNING: keep the secret key used in production secret!
# Use this py command to create secret 
# python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY = os.getenv('AZURE_SECRET_KEY')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['AZURE_POSTGRESQL_DATABASE'],
        'HOST': os.environ['AZURE_POSTGRESQL_HOST'],
        'USER': os.environ['AZURE_POSTGRESQL_USERNAME'],
        'PASSWORD': os.environ['AZURE_POSTGRESQL_PASSWORD'], 
    }
}


RQ_QUEUES = {
    'default': {
        'URL': os.environ['rqhost'],  # Redis server host
        'DB': 100,
        'DEFAULT_TIMEOUT': 3600,
    },
}


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
sentry_sdk.init(
    dsn=os.environ['sentry'],
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=False,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # To set a uniform sample rate
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production,
    profiles_sample_rate=1.0,
)
