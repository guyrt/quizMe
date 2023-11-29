from ninja import Router
from json import loads

from .auth import ApiKey

router = Router(auth=ApiKey())

@router.post("/writehtml")
def write_dom(request):
    print(f"made it")
    body = loads(request.body)
    import ipdb; ipdb.set_trace()
    return {'message': 'ok'}
