from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from .forms import FileUploadForm

from django.urls import reverse

class FileUploadView(FormView):
    form_class = FileUploadForm  # Define your custom form class
    template_name = 'privateuploads/upload_rfp.html'  # Template for the form

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        # Handle the uploaded file here (e.g., save it to a specific location or process it)
        # uploaded_file.content_type
        # handle pdf, zip, word.

        success_url = reverse('success_page', kwargs={'parameter_name': 1})
        
        return HttpResponseRedirect(success_url)
