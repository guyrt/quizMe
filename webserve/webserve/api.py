from ninja import NinjaAPI
from django.conf import settings

from extensionapis.api import router as extension_router
from quizzes.api import router as quiz_router
from users.api import router as user_router
from mltrack.api import router as mltrack_router


if settings.DEBUG:
    api = NinjaAPI()
else:
    api = NinjaAPI(docs_url=None)


api.add_router("browser", extension_router)
api.add_router("quiz", quiz_router)
api.add_router("user", user_router)
api.add_router("ml", mltrack_router)
