import markdown

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from customermodels.forms import LargeTextForm
from customermodels.models import UserSchema
from customermodels.parsers import create_user_table_from_yaml, user_schema_to_markdown


@login_required
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
