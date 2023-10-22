from uuid import uuid4

from azurewrapper.rfp.rawdocs_handler import RfpRawBlobHander
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import FormView
from privateuploads.doc_parser import RawDocParser

from .forms import FileUploadForm
from .models import DocumentCluster, RawUpload


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
        uploaded_file : InMemoryUploadedFile = form.cleaned_data['file']
        clean_filetype = self._clean_type(uploaded_file.content_type)

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

        RawDocParser().parse(uploaded_file, raw_upload, clean_filetype)

        success_url = reverse('doc_cluster_detail', kwargs={'id': doc_cluster.pk})
        
        return HttpResponseRedirect(success_url)

    def _clean_type(self, raw_type):
        if raw_type == 'application/pdf':
            return 'pdf'
        
        raise ValueError(f"Unexpected type {raw_type}")


class DocumentClusterListView(ListView):
    """todo - list all docs uploaded with 'analyze' buttons"""
    model = DocumentCluster  # Specify the model
    template_name = 'privateuploads/rfp_list.html'
    context_object_name = 'doc_cluster_list'

    def get_queryset(self):
        # Filter the objects to include only those marked as "active"
        return self.model.objects.filter(active=True)


class DocumentClusterDetailView(DetailView):
    """todo - list a single doc. show either 'processing' or show latest results"""
    model = DocumentCluster  # Specify the model
    template_name = 'privateuploads/rfp_detail.html'  # Specify the template for rendering
    context_object_name = 'doc_cluster'

    def get_queryset(self):
        # Filter the objects to include only those marked as "active"
        return self.model.objects.filter(active=True)


class DocumentClusterDeleteView(DeleteView):
    model = DocumentCluster  # Specify the model
    template_name = 'privateuploads/documentcluster_confirm_delete.html'  # Specify the template for confirmation
    success_url = reverse_lazy('doc_cluster_list')  # Redirect after deletion

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False  # Set the object as inactive
        self.object.save()
        return super(DocumentClusterDeleteView, self).delete(request, *args, **kwargs)
