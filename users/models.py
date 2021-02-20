from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.utils.crypto import get_random_string
import hashlib 
import base64

sg = SendGridAPIClient(settings.SENDGRID_HOST_PASSWORD)


def random_string():
    return get_random_string(8)


class Puzzle(models.Model):
    text = models.TextField()
    regex_answer = models.CharField(max_length=1000)
    max_points = models.IntegerField()

    def __str__(self):
        return self.text


class PuzzleTeam(models.Model):
    name = models.CharField(max_length=100, default="New Team")
    unique_code = models.CharField(
        max_length=100, unique=True, default=random_string)

    def __str__(self):
        return self.name


class PuzzleSolution(models.Model):
    team = models.ForeignKey(
        PuzzleTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name="solutions")

    puzzle = models.ForeignKey(
        Puzzle, on_delete=models.SET_NULL, null=True, blank=True, related_name="solutions")

    most_recent_solution = models.CharField(max_length=1000)
    locked = models.BooleanField(default=False)
    num_attempts = models.IntegerField()
    points_earned = models.DecimalField(
        default=0.0, decimal_places=4, max_digits=8)
    previous_attempts = models.CharField(max_length=2000, default="")

    def __str__(self):
        return "{} - {}".format(self.puzzle, self.team)


class User(AbstractUser):

    email = models.EmailField(unique=True)

    is_hacker = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)

    is_judge = models.BooleanField(default=False)

    organization = models.ForeignKey(
        'judging.Organization', on_delete=models.SET_NULL, null=True, blank=True)

    team = models.ForeignKey(
        PuzzleTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

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

    raffle_tickets = models.DecimalField(max_digits=7, decimal_places=3, default=0)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    @property
    def raffle_id(self):
        return base64.b64encode(self.email.encode('ascii')).decode('utf-8')

    def __str__(self):
        return self.email


class EmailView(models.Model):
    uuid_confirmation = models.UUIDField(default=uuid.uuid1)
    subject = models.CharField(max_length=1000, default="")
    message = models.CharField(max_length=20000, default="")
    action = models.CharField(max_length=1000, default="")
    redirect_url = models.CharField(max_length=1000, default="")

    sent = models.DateTimeField(
        auto_now_add=True, verbose_name="Sent Date (in UTC)")
    viewed = models.DateTimeField(
        auto_now_add=True, verbose_name="Viewed Date (in UTC)")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def send_email(self):
        email = Mail(from_email=settings.SENDGRID_FROM_EMAIL,
                     to_emails=self.user.email, subject=self.subject, html_content=self.message)
        try:
            response = sg.send(email)
            print(response)
            print(response.status_code)
            self.sent = datetime.now()
        except Exception as e:
            print(e.message)
        self.save()

    def __str__(self):
        return "Email - Subject: {}, User: {}".format(self.subject, self.user)


class Ticket(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tickets")

    question = models.CharField(max_length=10000, default="")
    location = models.CharField(max_length=10000, default="")

    contact = models.CharField(max_length=10000, default="")
    status = models.CharField(max_length=1000, default="")

    mentor = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="mentor_tickets", blank=True, null=True)

    slack_ts = models.CharField(max_length=40, default="")

    def __str__(self):
        return '{}'.format(self.question)
