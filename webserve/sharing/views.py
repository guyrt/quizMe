from django.http import Http404
from django.views.generic import RedirectView
from django.urls import reverse

from .models import ShareRequest

class ShareLandingRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Your dynamic logic to determine the URL
        guid = kwargs.get('guid')

        try:
            obj = ShareRequest.objects.get(active=1, share_link=guid)
        except ShareRequest.DoesNotExist:
            raise Http404()
        
        if obj.shared_object == 'privateuploads.models.DocumentCluster':
            return reverse('doc_cluster_feedback', guid)

        raise Http404()
