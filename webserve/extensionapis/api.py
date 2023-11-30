from ninja import Router
from json import loads

from .auth import ApiKey
from users.key_manager import EncryptionWrapper

router = Router(auth=ApiKey())

@router.post("/writehtml")
def write_dom(request):
    body = loads(request.body)
    encrypt = EncryptionWrapper()
    secret_dom = encrypt.encrypt(body['dom'])

    # Save a Raw File Save and upload.
    # Assume on server side we need to save (maybe relax later)

    # fire a task to parse
    

    return {'message': 'ok'}
