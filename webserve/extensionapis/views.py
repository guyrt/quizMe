# This file contains web views. Associated APIs are defined in ./api.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from mltrack.consumer_prompt_models import UserLevelVectorIndex
from .models import SingleUrl, SingleUrlFact


@login_required
def singleurl_list(request):
    singleurls = SingleUrl.objects.filter(user=request.user).order_by("-date_modified")
    singleurls = singleurls.annotate_with_titles()

    paginator = Paginator(singleurls, 20)  # Set the number of items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "extensionapis/singleurl_list.html",
        {"page_obj": page_obj, "expected_type": "singleurl"},
    )


@login_required
def single_url_detail(request, guid):
    single_url = get_object_or_404(SingleUrl, id=guid, user=request.user)
    single_url_facts = SingleUrlFact.objects.filter(base_url=single_url)

    ulv = UserLevelVectorIndex.objects.filter(doc_id=single_url.id)

    return render(
        request,
        "extensionapis/singleurl_detail.html", 
        {
            "single_url": single_url,
            "single_url_facts": single_url_facts,
            "vectors": ulv
        }
    )


@login_required
def process_content_template(request, guid):
    # queue it

    # redirect
    pass
