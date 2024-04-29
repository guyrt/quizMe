import os
from .shared_settings import *  # noqa: F403

ALLOWED_HOSTS = ["web", "localhost", "0.0.0.0", "127.0.0.1"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("AZURE_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["AZURE_POSTGRESQL_DATABASE"],
        "HOST": os.environ["AZURE_POSTGRESQL_HOST"],
        "USER": os.environ["AZURE_POSTGRESQL_USERNAME"],
        "PASSWORD": os.environ["AZURE_POSTGRESQL_PASSWORD"],
    }
}

# Dev!
# AZURE_POSTGRESQL_DATABASE="postgres"
# AZURE_POSTGRESQL_HOST="pgsql"
# AZURE_POSTGRESQL_USERNAME="postgressu"
# AZURE_POSTGRESQL_PASSWORD="mosdumps123"


RQ_QUEUES = {
    "default": {
        #        'URL': os.environ['rqhost'],
        "HOST": os.environ["rqhost"],  # Redis server host
        "PORT": 6379,  # Redis server port
        "DB": 0,
        "DEFAULT_TIMEOUT": 3600,
    },
}


STRIPE_URL = "https://buy.stripe.com/test_eVag2H7Yt6NUdK8fYY?prefilled_email={email}"
