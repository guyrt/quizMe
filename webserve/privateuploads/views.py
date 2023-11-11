import logging
from typing import Any
from uuid import uuid4

from django.db import models

from azurewrapper.rfp.rawdocs_handler import KMRawBlobHander
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, View
from django.views.generic.edit import FormView
from django_rq import enqueue
from mltrack.models import PromptResponse
from privateuploads.doc_parser import RawDocParser
from rfp_utils.raw_doc_parser import execute_doc_parse

from .forms import FileUploadForm
from .models import (DocumentCluster, DocumentClusterRoleChoices, DocumentFile,
                     RawUpload)

logger = logging.getLogger('webstack')


class FileUploadView(LoginRequiredMixin, FormView):
    form_class = FileUploadForm  # Define your custom form class
    template_name = 'privateuploads/upload_file.html'  # Template for the form

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        doc_type = self.request.GET.get('type', 'rfp')
        context['expected_type'] = doc_type
        context['all_types'] = DocumentClusterRoleChoices
        return context

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
        blob_handler = KMRawBlobHander()
        container, path = blob_handler.upload(uploaded_file, full_path, clean_filetype)

        # Create object.
        doc_cluster = DocumentCluster(
            owner=self.request.user,
            document_role=form.cleaned_data['form_type']
        )
        doc_cluster.save()

        raw_upload = RawUpload(
            document=doc_cluster,
            format=clean_filetype,
            location_container=container,
            location_path=path
        )
        raw_upload.save()

        docs = RawDocParser().parse(uploaded_file, raw_upload, clean_filetype)

        # start a queued work item.
        for doc in docs:
            result = enqueue(execute_doc_parse, doc.id)
            doc.last_jobid = result.id
            doc.save()

        # todo - on type
        success_url = reverse('doc_cluster_detail', kwargs={'pk': doc_cluster.pk})
        
        return HttpResponseRedirect(success_url)

    def _clean_type(self, raw_type):
        if raw_type == 'application/pdf':
            return 'pdf'
        
        raise ValueError(f"Unexpected type {raw_type}")


class RFPClusterListView(LoginRequiredMixin, ListView):
    """todo - list all docs uploaded with 'analyze' buttons"""
    model = DocumentCluster  # Specify the model
    template_name = 'privateuploads/rfp_list.html'
    context_object_name = 'doc_cluster_list'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        doc_type = self.request.path.split('/')[-1]

        logger.debug("Loading list from %s", doc_type)

        context['expected_type'] = doc_type
        return context

    def get_queryset(self):
        doc_type = self.request.path.split('/')[-1]
        return self.model.objects.filter(owner=self.request.user).filter(active=True).filter(document_role=doc_type)


class DocumentClusterDetailView(LoginRequiredMixin, DetailView):
    """todo - list a single doc. show either 'processing' or show latest results"""
    model = DocumentCluster  # Specify the model
    context_object_name = 'doc_cluster'

    def get_template_names(self) -> list[str]:
        if self.object.document_role == 'rfp':
            return ['privateuploads/rfp_detail.html']
        if self.object.document_role == 'proposal':
            return ['privateuploads/proposal_detail.html']
        raise NotImplementedError(f"Need to do {self.object.document_role}")

    def get_queryset(self):
        # Filter the objects to include only those marked as "active" to prevent pulling others.
        return super().get_queryset().filter(owner=self.request.user).filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get all your prompts.
        prompts = list(PromptResponse.objects.filter(document_inputs__docfile__document=self.object).filter(document_inputs__active=1))

        # Add additional context data
        prompts_d = {
            p.output_role: p
            for p in prompts
        }

        context['prompts'] = prompts_d
        context['all_prompts'] = prompts
        return context


class DocumentClusterDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentCluster  # Specify the model
    template_name = 'privateuploads/documentcluster_confirm_delete.html'  # Specify the template for confirmation
    
    # todo - fix
    success_url = reverse_lazy('rfp_list')  # Redirect after deletion

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False  # Set the object as inactive
        self.object.save()
        return super(DocumentClusterDeleteView, self).delete(request, *args, **kwargs)


class DocumentClusterReprocessView(LoginRequiredMixin, View):

    def post(self, request, pk):
        objs = DocumentFile.objects.filter(active=True).filter(document__id=pk)
        for doc in objs:
            result = enqueue(execute_doc_parse, doc.id)
            doc.last_jobid = result.id
            doc.save()
        return JsonResponse({'message': f'Reprocessing {len(objs)} documents.'})


class DocumentClusterRawView(LoginRequiredMixin, DetailView):

    model = DocumentCluster

    def render_to_response(self, context, **response_kwargs):
        my_object = self.get_object()
        doc_file = my_object.documentfile_set.get()
        extract = doc_file.documentextract_set.filter(active=1).get()
        raw_text = extract.as_html()
        response = self.get_response(raw_text, **response_kwargs)

        return response

    def get_response(self, raw_text, **response_kwargs):
        response = HttpResponse(raw_text, content_type='text/html')
        response.status_code = 200
        return response
    

class DocumentClusterCreateShareView(LoginRequiredMixin, View):

    def post(self, request, pk):
        objs = DocumentFile.objects.filter(active=True).filter(document__id=pk)
        return JsonResponse({'share': f'https://www.google.com'})
