from django import forms
from django.core.validators import FileExtensionValidator

from privateuploads.models import DocumentClusterRoleChoices

class FileUploadForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'xlsx', 'zip'])]
    )

    form_type = forms.ChoiceField(required=True, initial='rfp', choices=DocumentClusterRoleChoices)
