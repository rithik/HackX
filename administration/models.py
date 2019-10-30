from django.db import models
from django.conf import settings
import datetime 
from pytz import timezone

class Settings(models.Model):
    '''
    APPLICATION_SUBMISSION_DEADLINE = tz.localize(datetime.datetime(2019, 11, 20, 23, 59, 59, 0))
    APPLICATION_SUBMISSION_DEADLINE_FMT = APPLICATION_SUBMISSION_DEADLINE.strftime("%B %d, %Y %I:%M:%S %Z")

    APPLICATION_CONFIRMATION_DEADLINE = tz.localize(datetime.datetime(2019, 11, 21, 23, 59, 59, 0))
    APPLICATION_CONFIRMATION_DEADLINE_FMT = APPLICATION_CONFIRMATION_DEADLINE.strftime("%B %d, %Y %I:%M:%S %Z")
    '''
    application_submission_deadline = models.DateTimeField(auto_now_add=True)
    application_confirmation_deadline = models.DateTimeField(auto_now_add=True)
    
    def application_submission_deadline_fmt(self):
        return self.application_submission_deadline.astimezone(settings.TZ).strftime("%B %d, %Y %I:%M %p %Z")
    
    def application_confirmation_deadline_fmt(self):
        return self.application_confirmation_deadline.astimezone(settings.TZ).strftime("%B %d, %Y %I:%M %p %Z")
