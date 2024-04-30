from django.urls import reverse
import markdown
from django_rq import enqueue

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, redirect, render

from customermodels.forms import LargeTextForm
from customermodels.jobs import fill_structured_info
from customermodels.models import ExtractionStatusChoices, RawDocumentExtract, UserSchema
from customermodels.parsers import create_user_table_from_yaml, user_schema_to_markdown
from extensionapis.models import SingleUrl


@login_required
@require_GET
def show_schema(request, pk):
    schema = get_object_or_404(UserSchema, pk=pk, user=request.user)
    schema_md = user_schema_to_markdown(request.user, pk)
    schema_html = markdown.markdown(schema_md, extensions=["tables"])
    return render(
        request,
        "customermodels/schema_view.html",
        {"schema_md": schema_md, "schema": schema, "schema_html": schema_html},
    )


@login_required
def create_dataschema(request):
    if request.method == "POST":
        form = LargeTextForm(request.POST)
        if form.is_valid():
            # Here, you can process the content, for example, save it to the database
            parsed_content = form.cleaned_data["content"]
            schema = create_user_table_from_yaml(request.user, parsed_content)
            # Redirect or handle the content as needed
            return redirect("schema_details", pk=str(schema.pk))
    else:
        form = LargeTextForm()

    return render(request, "customermodels/create_view.html", {"form": form})


@login_required
@require_GET
def show_extractions(request, guid):
    extraction = get_object_or_404(RawDocumentExtract, id=guid, owner=request.user)
    return render(request, "customermodels/raw_document_extract_details.html", {'extract': extraction})


@login_required
@require_GET
def process_content_template(request, guid):
    single_url = get_object_or_404(SingleUrl, id=guid, user=request.user)

    extraction = RawDocumentExtract(
        owner=request.user,
        source_table='single_url',
        source_pk=single_url.pk,
        extracted_content = '',
        extraction_status = ExtractionStatusChoices.InProgress,
        extraction_model_details = ''
    )
    extraction.save()

    # queue it
    enqueue(fill_structured_info, str(extraction.pk))

    # redirect
    return redirect(reverse('show_content_extract', guid=extraction.pk))
