from django.http import Http404, JsonResponse
from django.views.generic import RedirectView
from django.urls import reverse

from .forms import FeedbackForm
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
            return reverse('doc_cluster_feedback', kwargs={'guid': obj.share_link})

        raise Http404()


def feedback_submit(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()  # Save the feedback to the database
            return JsonResponse({'message': 'Feedback submitted successfully'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
