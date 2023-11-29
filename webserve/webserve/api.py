from ninja import NinjaAPI

from extensionapis.api import router as extension_router

api = NinjaAPI()
api.add_router("browser", extension_router)
