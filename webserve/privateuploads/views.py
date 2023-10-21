from uuid import uuid4

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import FormView

from webserve.privateuploads.models import DocumentCluster, RawUpload

from .forms import FileUploadForm

from azurewrapper.rfp.rawdocs_handler import RfpRawBlobHander


class FileUploadView(FormView):
    form_class = FileUploadForm  # Define your custom form class
    template_name = 'privateuploads/upload_rfp.html'  # Template for the form

    def form_valid(self, form):
        """
        Create a new Documentcluster.
        Upload raw file to azure and create a rawupload.
        Kick a job to process the RawUpload to individual files.
        Kick a job to process further if user said to.
        """
        uploaded_file = form.cleaned_data['file']
        clean_filetype = self._clean_type(uploaded_file.format)

        full_path = f"{self.request.user.pk}/{uuid4()}/{uploaded_file.name}"
        blob_handler = RfpRawBlobHander()
        container, path = blob_handler.upload(uploaded_file, full_path)

        # Create object.
        doc_cluster = DocumentCluster(
            owner=self.request.user,
            upload_source='RFP'
        )
        doc_cluster.save()

        raw_upload = RawUpload(
            document=doc_cluster,
            format=clean_filetype,
            location_container=container,
            location_path=path
        )
        raw_upload.save()

        # queue up some work.

        success_url = reverse('success_page', kwargs={'parameter_name': 1})
        
        return HttpResponseRedirect(success_url)

    def _clean_type(self, raw_type):
        if raw_type == 'application/pdf':
            return 'pdf'
        
        raise ValueError(f"Unexpected type {raw_type}")


class DocumentClusterListView():
    """todo - list all docs uploaded with 'analyze' buttons"""
    pass


class DocumentClusterDetailView():
    """todo - list a single doc. show either 'processing' or show latest results"""
    pass
