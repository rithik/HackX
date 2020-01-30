from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import get_connection, send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.core.files import File

import glob
import uuid
from pytz import timezone
import pytz
from datetime import datetime
from applications.models import Application, Confirmation
from users.models import User, EmailView
from judging.models import Organization
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from . import nametag
from zipfile import ZipFile
import os
import json
import random
from itertools import product
from .models import Settings
import dropbox
import os
import slack
import tweepy

dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
slack_client = None
if settings.SLACK_ENABLED:
    slack_client = slack.WebClient(token=settings.SLACK_API_TOKEN)

if settings.TWITTER_ENABLED:
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

@login_required
def create_judges(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    if not settings.DEBUG:
        return JsonResponse({
            "message": "NOT IN DEBUG MODE - settings.DEBUG is False needs to be True"
        })
    if request.method == 'GET':
        first_names = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eliza',
                       'Frank', 'George', 'Helena', 'Isabelle', 'John']
        last_names = ['Schuyler', 'Washington', 'Hamilton',
                      'Adams', 'Madison', 'Franklin', 'Jefferson', 'Mulligan']

        # Generate notional number of judges per organization
        orgs = Organization.objects.all()
        organizers_id = Organization.objects.get(name="Organizers")
        avg_num_judges_per_org = 3
        judge_needs = []  # list of org ids, one for each judge needed
        for org in orgs:
            if org.id == organizers_id:
                continue
            for i in range(int(random.expovariate(1 / (avg_num_judges_per_org - 1))) + 1):
                judge_needs.append(org.id)

        # Create judges
        j_cnt = 0
        for fn, ln in product(first_names, last_names):
            org_id = judge_needs[j_cnt]
            username = fn[0].lower() + ln.lower()
            u = User.objects.create(first_name=fn, last_name=ln, username=username, email="{}-{}-{}@gmail.com".format(fn, ln, j_cnt),
                         organization=Organization.objects.get(id=org_id), is_judge=True)
            u.set_password('Qaz1235$')
            u.save()
            j_cnt += 1
            if j_cnt >= len(judge_needs):
                break
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def make_admin(request, user_id):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    try:
        h = User.objects.filter(id=user_id).first()
        h.is_admin = True
        h.is_superuser = True
        h.is_staff = True
        h.save()
        return JsonResponse({"status": 200, "message": "Success"})
    except:
        return JsonResponse({"status": 404, "message": "Error"})

@login_required
def make_admin_manual(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")

    if request.method == "GET":
        return render(request, "make-admin.html", {
            "highlight": "", 
            "user": u,
            "msg": "Please enter the admin password to make yourself an admin!"
        })

    if request.method == "POST":
        password = request.POST.get('password', '')
        if password == settings.ADMIN_PASSWORD:
            u.is_admin = True
            u.is_superuser = True
            u.is_staff = True
            u.save()
            return render(request, "make-admin.html", {
                "highlight": "", 
                "user": u,
                "msg": "You are now an admin!"
            })
        else:
            return render(request, "make-admin.html", {
                "highlight": "", 
                "user": u,
                "msg": "Incorrect Password! Try again!"
            })

@login_required
def make_volunteer_manual(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")

    if request.method == "GET":
        return render(request, "make-volunteer.html", {
            "highlight": "", 
            "user": u,
            "msg": "Please enter the volunteer password to make yourself a volunteer!"
        })

    if request.method == "POST":
        password = request.POST.get('password', '')
        if password == settings.VOLUNTEER_PASSWORD:
            u.is_volunteer = True
            u.save()
            return render(request, "make-volunteer.html", {
                "highlight": "", 
                "user": u,
                "msg": "You are now a volunteer!"
            })
        else:
            return render(request, "make-volunteer.html", {
                "highlight": "", 
                "user": u,
                "msg": "Incorrect Password! Try again!"
            })

@login_required
def admin_main(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin and not u.is_volunteer:
        return redirect("/dashboard")
    if u.is_volunteer:
        return redirect('/admin/qr')
    stats = get_stats()
    return render(request, "admin-stats.html", {
        "highlight": "admin", 
        "user": u,
        "stats": stats, 
        "adminHighlight": "stats"
    })

def get_stats():
    total = User.objects.count()
    hack0 = Application.objects.filter(hackathons=0).count()
    hack1 = Application.objects.filter(hackathons=1).count()
    hack2 = Application.objects.filter(hackathons=2).count()
    hack3 = Application.objects.filter(hackathons=3).count()
    hack4 = Application.objects.filter(hackathons=4).count()
    hack5 = Application.objects.filter(hackathons=5).count()
    hack6 = Application.objects.filter(hackathons=6).count()
    hack7 = Application.objects.filter(hackathons=7).count()
    hack8 = Application.objects.filter(hackathons=8).count()
    hack9 = Application.objects.filter(hackathons=9).count()

    schools = {}
    for a in Application.objects.all():
        if not a.school in schools:
            schools[a.school] = {
                "accepted": 0,
                "waitlisted": 0,
                "rejected": 0,
                "complete": 0,
                "confirmed": 0,
                "declined": 0
            }
        if a.accepted:
            schools[a.school]['accepted']+=1
        if a.waitlisted:
            schools[a.school]['waitlisted']+=1
        if a.rejected:
            schools[a.school]['rejected']+=1
        if a.app_complete:
            schools[a.school]['complete']+=1

    for c in Confirmation.objects.all():
        school = c.user.application.school
        if c.confirmed:
            schools[school]['confirmed']+=1
        if c.declined:
            schools[school]['declined']+=1

    return {
        "hackers": total,
        "verified": User.objects.filter(verified=True).count(),
        "submitted": Application.objects.filter(app_complete=True).count(),
        "admitted": Application.objects.filter(accepted=True).count(),
        "waitlisted": Application.objects.filter(waitlisted=True).count(),
        "rejected": Application.objects.filter(rejected=True).count(),
        "confirmed": Confirmation.objects.filter(confirmed=True).count(),
        "declined": Confirmation.objects.filter(declined=True).count(),
        "reimbursement": Application.objects.filter(travel=True).count(),
        "tshirt": "XS({}) S({}) M({}) L({}) XL({})".format(
            Confirmation.objects.filter(tshirt="XS").count(),
            Confirmation.objects.filter(tshirt="S").count(),
            Confirmation.objects.filter(tshirt="M").count(),
            Confirmation.objects.filter(tshirt="L").count(),
            Confirmation.objects.filter(tshirt="XL").count()
        ),
        "dietary": "Vegetarian({}) Vegan({}) Nut Allergy({}) Halal({}) Gluten Free({}) None({})".format(
            Confirmation.objects.filter(dietary="Vegetarian").count(),
            Confirmation.objects.filter(dietary="Vegan").count(),
            Confirmation.objects.filter(dietary="Nut Allery").count(),
            Confirmation.objects.filter(dietary="Halal").count(),
            Confirmation.objects.filter(dietary="Gluten Free").count(),
            Confirmation.objects.filter(dietary="None").count()
        ),
        "genders": {
            "male": Application.objects.filter(gender="Male").count(),
            "female": Application.objects.filter(gender="Female").count(),
            "other": Application.objects.filter(gender="Other").count()
        },
        "races": {
            "aa": Application.objects.filter(race="African American").count(),
            "ai": Application.objects.filter(race="American Indian").count(),
            "as": Application.objects.filter(race="Asian").count(),
            "h": Application.objects.filter(race="Hispanic").count(),
            "nh": Application.objects.filter(race="Native Hawaiian").count(),
            "w": Application.objects.filter(race="White").count(),
            "o": Application.objects.filter(race="Other").count(),
        },
        "hackathons":{
            "beg": hack0,
            "beg1": hack1 + hack2 + hack3,
            "med2": hack4 + hack5 + hack6,
            "exp3": hack7 + hack8 + hack9,
            "expert4": total - (hack0 + hack1 + hack2 + hack3 + hack4 + hack5
                + hack6 + hack7 + hack8 + hack9)
        },
        "schools": schools
    }

@login_required
def admin_users(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    return render(request, "admin-users.html", {
        "highlight": "admin",
        "all_hackers": User.objects.all(), 
        "user": u,
        "adminHighlight": "users"
    })

@login_required
def admin_qr(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin and not u.is_volunteer:
        return redirect("/dashboard")
    highlight = "admin" if u.is_admin else "volunteer"
    return render(request, "qr.html", {
        "highlight": highlight, 
        "user": u,
        "adminHighlight": "qr"
    ,})

@login_required
def admin_qr_settings(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin and not u.is_volunteer:
        return redirect("/dashboard")
    highlight = "admin" if u.is_admin else "volunteer"
    return render(request, "qr-settings.html", {
        "highlight": highlight, 
        "user": u,
        "all_hackers": [u for u in User.objects.all() if hasattr(u, 'confirmation') and u.confirmation.confirmed],
        "adminHighlight": "qr-settings"
    })

@login_required
def admin_make_nametags(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    metadata, zip_file = dbx.files_download_zip("/Nametags/")
    response = HttpResponse(zip_file.content, content_type="application/zip")
    response['Content-Disposition'] = 'inline; filename=' + 'nametags.zip'
    return response


@login_required
def qr_request(request, typ, num, tf):
    if tf == "true":
        tf = True
    else:
        tf = False
    p = User.objects.filter(qr_hash=num)
    if p.count() == 0:
        return JsonResponse({
            "approved": False,
            "error": "ERROR - no user found"
        })
    else:
        p = p.first()
    err = ""
    if typ == "check-in":
        if p.checked_in:
            err = "already checked in"
        p.checked_in = tf
    elif typ == "sat-breakfast":
        if p.sat_breakfast:
            err = "already ate Saturday breakfast"
        p.sat_breakfast = tf
    elif typ == "sat-lunch":
        if p.sat_lunch:
            err = "already ate Saturday lunch"
        p.sat_lunch = tf
    elif typ == "sat-dinner":
        if p.sat_dinner:
            err = "already ate Saturday dinner"
        p.sat_dinner = tf
    elif typ == "sun-breakfast":
        if p.sun_breakfast:
            err = "already ate Sunday breakfast"
        p.sun_breakfast = tf
    elif typ == "sun-lunch":
        if p.sun_lunch:
            err = "already ate Sunday lunch"
        p.sun_lunch = tf
    else:
        return JsonResponse({
            "name": p.application.full_name,
            "approved": False,
            "dietary": p.confirmation.dietary,
            "error": "ERROR - request type not found"
        })
    if not err == "" and tf == True:
         return JsonResponse({
             "approved": False,
             "error": "ERROR - " + p.application.full_name + " has " + err,
         })
    p.save()

    req_response = {
        "qr": num,
        "typ": typ, 
        "tf": tf,
        "type": "qr-change"
    }

    layer = get_channel_layer()
    async_to_sync(layer.group_send)('chat_qr', {
        'type': 'chat_message',
        'message': json.dumps(req_response)
    })

    # socketio.emit('qr-change', req_response, broadcast=True)
    return JsonResponse({
        "name": p.application.full_name,
        "approved": True,
        "dietary": p.confirmation.dietary,
        "error": "none",
        "tshirt": p.confirmation.tshirt
    })

@login_required
def accept_user(request, user_id):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    try:
        h = User.objects.filter(id=user_id).first()
        a = h.application
        a.accepted = True
        a.waitlisted = False
        a.rejected = False

        try:
            if not h.confirmation:
                c = Confirmation.objects.create(user=h)
        except:
            c = Confirmation.objects.create(user=h)

        email_uuid = uuid.uuid1()
        e = EmailView.objects.create(
            uuid_confirmation=email_uuid, 
            subject="HooHacks Status Update", 
            message=settings.ACCEPTED_EMAIL.format(h.application.full_name, Settings.objects.all()[0].application_submission_deadline_fmt(), settings.PROD_URL, email_uuid),
            action="accepted",
            redirect_url="/dashboard",
            user=h
        )
        e.send_email()
        print(e.uuid_confirmation)
        
        a.save()
        h.save()
        return JsonResponse({"status": 200, "message": "Success"})
    except:
        return JsonResponse({"status": 404, "message": "Error"})

@login_required
def waitlist_user(request, user_id):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    try:
        h = User.objects.filter(id=user_id).first()
        a = h.application
        a.accepted = False
        a.waitlisted = True
        a.rejected = False

        # if h.confirmation:
        #     c = u.confirmation
        #     c.delete()

        email_uuid = uuid.uuid1()
        e = EmailView.objects.create(
            uuid_confirmation=email_uuid, 
            subject="HooHacks Status Update", 
            message=settings.WAITLISTED_EMAIL.format(h.application.full_name),
            action="waitlisted",
            redirect_url="/dashboard",
            user=h
        )
        e.send_email()
        print(e.uuid_confirmation)
        
        a.save()
        return JsonResponse({"status": 200, "message": "Success"})
    except:
        return JsonResponse({"status": 404, "message": "Error"})

@login_required
def reject_user(request, user_id):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    try:
        h = User.objects.filter(id=user_id).first()
        a = h.application
        a.accepted = False
        a.waitlisted = False
        a.rejected = True

        #if h.confirmation:
        #   c = u.confirmation
        #   c.delete()

        email_uuid = uuid.uuid1()
        e = EmailView.objects.create(
            uuid_confirmation=email_uuid, 
            subject="HooHacks Status Update", 
            message=settings.REJECTED_EMAIL.format(h.application.full_name),
            action="rejected",
            redirect_url="/dashboard",
            user=h
        )
        e.send_email()
        print(e.uuid_confirmation)
        
        a.save()
        return JsonResponse({"status": 200, "message": "Success"})
    except:
        return JsonResponse({"status": 404, "message": "Error"})

@login_required
def view_organizations(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin:
        return redirect("/dashboard")
    if request.method == "GET":
        return render(request, "organizations.html",{
            "organizations": Organization.objects.all(),
            "highlight": "admin", 
            "user": u,
            "adminHighlight": "organizations"
        })
    if request.method == "POST":
        add = request.POST.get('add', False)
        update = request.POST.get('update', False)
        delete = request.POST.get('delete', False)
        if add == "true":
            add = True
        if add:
            name = request.POST.get('name', '')
            o = Organization.objects.create(name=name)
            return JsonResponse({
                'message': "success",
                "org_id": o.id,
                "org_name": o.name
            })
        if update == "true":
            update = True
        if update:
            name = request.POST.get('name', '')
            id = request.POST.get('oid', '')
            o = Organization.objects.get(id=id)
            o.name = name
            o.save()
            return JsonResponse({
                'message': "success",
                "org_id": o.id,
                "org_name": o.name
            })
        if delete == "true":
            delete = True
        if delete:
            id = request.POST.get('oid', '')
            o = Organization.objects.get(id=id)
            o.delete()
            return JsonResponse({
                'message': "success",
                "org_id": o.id,
                "org_name": o.name
            })
        
@login_required
def admin_settings(request):
    if not request.user.is_admin:
        return redirect('/')

    if request.method == "GET":
        s = Settings.objects.all()[0]
        return render(request, 'admin-settings.html', {
            "application_submission_date": s.application_submission_deadline.astimezone(settings.TZ).strftime("%Y-%m-%dT%H:%M"),
            "application_confirmation_date": s.application_confirmation_deadline.astimezone(settings.TZ).strftime("%Y-%m-%dT%H:%M"),
            "judging_deadline": s.judging_deadline.astimezone(settings.TZ).strftime("%Y-%m-%dT%H:%M"),
            "highlight": "admin", 
            "adminHighlight": "settings"
        })
    
    if request.method == "POST":
        submission_deadline = request.POST.get('submission_deadline', None)
        confirmation_deadline = request.POST.get('confirmation_deadline', None)
        judging_deadline = request.POST.get('judging_deadline', None)
        s = Settings.objects.all()[0]
        s.application_submission_deadline = settings.TZ.localize(datetime.strptime(submission_deadline, "%Y-%m-%dT%H:%M"))
        s.application_confirmation_deadline = settings.TZ.localize(datetime.strptime(confirmation_deadline, "%Y-%m-%dT%H:%M"))
        s.judging_deadline = settings.TZ.localize(datetime.strptime(judging_deadline, "%Y-%m-%dT%H:%M"))
        s.save()
        return JsonResponse({
            'message': 'success'
        })

@login_required
def send_notification(request):
    if not request.user.is_admin:
        return JsonResponse({"status": 403, "message": "User is not an admin!"})
    if request.POST.get('notification_msg', '') == '':
        return JsonResponse({"status": 403, "message": "There is no notification message!"})

    success_msg = ""
    msg = request.POST.get('notification_msg', '')

    if settings.SLACK_ENABLED:
        response = slack_client.chat_postMessage(
            channel=settings.SLACK_NOTIFICATIONS_CHANNEL,
            text=msg)
        success_msg += "Notification published to Slack! "
    
    if settings.TEXTING_ENABLED:
        all_confirmations = Confirmation.objects.all()
        subject = '{} Announcement'.format(settings.EVENT_NAME)
        connection = get_connection(host=settings.SENDGRID_HOST, 
                                    port=settings.SENDGRID_PORT, 
                                    username=settings.SENDGRID_HOST_USER, 
                                    password=settings.SENDGRID_HOST_PASSWORD, 
                                    use_tls=False) 

        for confirmation in all_confirmations:
            if confirmation.carrier != 'Other':
                email_addr = confirmation.phone + settings.CARRIER_EMAIL_LOOKUP[confirmation.carrier]
                send_mail(subject, msg, settings.TEXTING_FROM_EMAIL, [email_addr], connection=connection)
        success_msg += "Notification sent via text! "

        connection.close()
    
    if settings.TWITTER_ENABLED:
        api.update_status(msg)
        success_msg += "Notification published on Twitter! "

    return JsonResponse({"status": 200, "message": success_msg})
