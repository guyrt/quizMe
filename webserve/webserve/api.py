from ninja import NinjaAPI

from extensionapis.api import router as extension_router
from quizzes.api import router as quiz_router

api = NinjaAPI()
api.add_router("browser", extension_router)
api.add_router("quiz", quiz_router)
