from django import forms
from django.core.validators import FileExtensionValidator

class FileUploadForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'xlsx', 'zip'])]
    )
    analyze = forms.BooleanField(required=False, initial=True)