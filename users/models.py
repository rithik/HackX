from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import uuid 

class User(AbstractUser):

    email = models.EmailField(unique=True)

    is_hacker = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)

    is_judge = models.BooleanField(default=False)

    organization = models.ForeignKey('judging.Organization', 
        on_delete=models.CASCADE, null=True, blank=True)
    sd_offset = models.DecimalField(max_digits=9, decimal_places=5, default=0)

    first_name = models.CharField(max_length=1000, default="")
    last_name = models.CharField(max_length=1000, default="")
    login_hash = models.CharField(max_length=1000, default="")

    verified = models.BooleanField(default=False)

    qr_hash = models.UUIDField(default=uuid.uuid1)
    checked_in = models.BooleanField(default=False)
    sat_breakfast = models.BooleanField(default=False)
    sat_lunch = models.BooleanField(default=False)
    sat_dinner = models.BooleanField(default=False)
    sun_breakfast = models.BooleanField(default=False)
    sun_lunch = models.BooleanField(default=False)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.email

class EmailView(models.Model):
    uuid_confirmation = models.UUIDField(default=uuid.uuid1)
    subject = models.CharField(max_length=1000, default="")
    message = models.CharField(max_length=20000, default="")
    action = models.CharField(max_length=1000, default="") 
    redirect_url = models.CharField(max_length=1000, default="")

    sent = models.DateTimeField(auto_now_add=True, verbose_name="Sent Date (in UTC)")
    viewed = models.DateTimeField(auto_now_add=True, verbose_name="Viewed Date (in UTC)")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def send_email(self):
        send_mail(self.subject, self.message, settings.EMAIL_HOST_USER, [self.user.email], html_message=self.message)
        self.sent = datetime.now()
        self.save()

    def __str__(self):
        return "Email - Subject: {}, User: {}".format(self.subject, self.user)

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")

    question = models.CharField(max_length=10000, default="")
    location = models.CharField(max_length=10000, default="")

    contact = models.CharField(max_length=10000, default="")
    status = models.CharField(max_length=1000, default="")

    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentor_tickets", blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.question)
