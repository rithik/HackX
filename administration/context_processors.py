from django.conf import settings
from django.http import HttpResponse

def event_name(request):
    return {'event_name' : settings.EVENT_NAME}

def contact_email(request):
    return {'contact_email' : settings.CONTACT_EMAIL}
