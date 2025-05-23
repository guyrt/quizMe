"""
ASGI config for webserve project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

settings_module = (
    "webserve.production_settings"
    if "RUNNING_IN_PRODUCTION" in os.environ
    else "webserve.dev_settings"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_asgi_application()
