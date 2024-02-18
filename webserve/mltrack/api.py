from ninja import Router, pagination
from django_rq import enqueue

from pydantic import UUID4
from mltrack.schemas import UserLevelVectorIndexSchema
from users.apiauth import ApiKey
from extensionapis.models import SingleUrl
from mltrack.consumer_prompt_models import UserLevelVectorIndex
from parser_utils.webutils.freeassociate_parser_driver import process_raw_doc

from typing import List


router = Router(auth=[ApiKey()], tags=['ml'])

@router.post("/reprocess")
def write_dom(request):
    urls = SingleUrl.objects.filter(user=request.auth)
    for url in urls:
        enqueue(process_raw_doc, url.pk)
    return {'num_docs': len(urls)}

@router.post("/chunks/{url_id}", response=List[UserLevelVectorIndexSchema])
def get_chunks(request, url_id : UUID4):
    return UserLevelVectorIndex.objects.filter(user=request.auth).filter(doc_id=url_id)
