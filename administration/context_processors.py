from django.conf import settings
from django.http import HttpResponse

def event_name(request):
    return {'event_name' : settings.EVENT_NAME}
