from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from users.models import User, EmailView
from pytz import timezone
from datetime import datetime

def receive_email(request, email_uuid):
    e = EmailView.objects.filter(uuid_confirmation=email_uuid).first()
    u = e.user
    tz = timezone('US/Eastern')
    e.viewed = tz.localize(datetime.now())
    if e.action == "verify":
        u.verified = True
    e.save()
    u.save()
    return redirect(e.redirect_url)
    