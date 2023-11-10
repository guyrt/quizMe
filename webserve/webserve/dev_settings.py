from .shared_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-h@6nuzpckf*1wa1sb3ufd79ag#cjx#p^sg4%w^@x7pa6h-j6!0"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


RQ_QUEUES = {
    'default': {
        'URL': os.environ['rqhost'],
        'DB': 0,
        'DEFAULT_TIMEOUT': 3600,
    },
}
