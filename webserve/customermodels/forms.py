from django import forms
from django.core.exceptions import ValidationError
import yaml

from customermodels.schemas import UserSchemaSchema


class LargeTextForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 10, "cols": 80}))

    def clean_content(self) -> UserSchemaSchema:
        content = self.cleaned_data["content"]
        try:
            parsed_content = yaml.safe_load(content)
            config = UserSchemaSchema.model_validate(parsed_content)
        except yaml.YAMLError:
            raise ValidationError(
                "The provided content is not valid YAML. Please correct it and try again."
            )
        except ValidationError as e:
            # Pydantic's ValidationError can be converted to a string that includes all errors
            raise ValidationError(f"Validation error in YAML structure: {e}")
        return config
