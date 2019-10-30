from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

import uuid
from pytz import timezone
from datetime import datetime
from .models import Application, Confirmation
from users.models import User, EmailView
import dropbox 
from administration.models import Settings

dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

@login_required
def application(request):
    ALLOW = True
    tz = timezone('US/Eastern')
    if tz.localize(datetime.now()) >= Settings.objects.all()[0].application_submission_deadline:
        ALLOW = False
    u = request.user
    a = u.application
    if not request.user.is_authenticated:
        return redirect("/logout")
    if not request.method == "POST":
        return render(request, "application.html", {
            "user": u, 
            "app": a,
            "schools": settings.SCHOOLS, 
            "genders": settings.GENDERS,
            "races": settings.RACES, 
            "grad_year": settings.GRADUATION_YEARS,
            "highlight": "application",
            "travel_methods": settings.TRAVEL_METHODS, 
            "msg": "", 
            "allow": ALLOW
        })
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')
        if button_type == "travel":
            travel = request.POST.get('travel', '')
            where_from = request.POST.get('where-from', '')
            travel_method = request.POST.get('travel-method', '')
            miles = request.POST.get('miles', '')
            cost = request.POST.get('cost', '')
            if travel == "on":
                a.travel = True
                a.where_from = where_from
                a.travel_method = travel_method
                a.miles = miles
                a.cost = cost
            else:
                a.travel = False
            a.save()
            return render(request, "application.html", {
                "user": u, 
                "app": a,
                "schools": settings.SCHOOLS, 
                "genders": settings.GENDERS,
                "races": settings.RACES, 
                "grad_year": settings.GRADUATION_YEARS,
                "highlight": "application",
                "travel_methods": settings.TRAVEL_METHODS, 
                "msg": "Your travel application has been submitted!", 
                "allow": ALLOW
            })

        full_name = request.POST.get('full-name', '')
        birthday = request.POST.get('birthday', '')
        school = request.POST.get('school', '')
        grad_year = request.POST.get('grad-year', '')
        gender = request.POST.get('gender', '')
        race = request.POST.get('race', '')
        describe = request.POST.get('describe', '')
        major = request.POST.get('major', '')
        hackathons = request.POST.get('hackathons', '')
        why = request.POST.get('why', '')
        mlh = request.POST.get('mlh', '')

        a.full_name = full_name
        a.birthday = birthday
        a.school = school
        a.grad_year = grad_year
        a.gender = gender
        a.race = race
        a.describe = describe
        a.major = major
        a.hackathons = hackathons
        a.why = why

        if mlh == "on":
            a.mlh_rules = True
        else:
            a.mlh_rules = False

        a.app_complete = True
        u.full_name = full_name
        
        u.save()
        a.save()
        
        return render(request, "application.html", {
            "user": u, 
            "app": a,
            "schools": settings.SCHOOLS, 
            "genders": settings.GENDERS,
            "races": settings.RACES, 
            "grad_year": settings.GRADUATION_YEARS,
            "highlight": "application",
            "travel_methods": settings.TRAVEL_METHODS, 
            "msg": "Your application has been submitted!", 
            "allow": ALLOW
        })

@login_required
def confirmation(request):
    u = request.user
    a = u.application
    c = u.confirmation
    tz = timezone('US/Eastern')
    if not a.accepted:
        return JsonResponse({
            'message': 'Not authorized'
        })
    ALLOW = True
    if tz.localize(datetime.now()) >= Settings.objects.all()[0].application_confirmation_deadline:
        ALLOW = False
    if not u:
        return redirect("/logout")
    if not request.method == "POST":
        return render(request, "confirmation.html", {
            "user": u, 
            "app": a, 
            "c": c, 
            "highlight": "confirmation",
            "tshirt_sizes": settings.TSHIRT_SIZES, 
            "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
            "msg": "", 
            "allow": ALLOW
        })
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')
        if button_type == "decline":
            c.declined = True
            c.confirmed = False
            c.save()
            return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "msg": "Your confirmation application has been submitted!", 
                "allow": ALLOW
            })
            
        tshirt = request.POST.get('tshirt', '')
        dietary = request.POST.get('dietary', '')
        phone = request.POST.get('phone', '')
        github = request.POST.get('github', '')
        notes = request.POST.get('notes', '')
        file = request.FILES['file']
        print(file)
        if file == '':
            return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "msg": "", 
                "allow": ALLOW
            })

        file_path = ""
        if file:
            file_path = '/Resumes/' + str(a.grad_year) + '/' + u.full_name + '-Resume.pdf'
            if not c.resume_file_name == "":
                dbx.files_delete_v2(file_path)
            dbx.files_upload(file.file.read(), file_path)
        else:
            return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "msg": "", 
                "allow": ALLOW
            })

        c.resume_file_name = file_path
        c.tshirt = tshirt
        c.dietary = dietary
        c.phone = phone
        c.github = github
        c.notes = notes
        c.confirmed = True
        c.declined = False
        c.save()

        email_uuid = uuid.uuid1()

        e = EmailView.objects.create(
            uuid_confirmation=email_uuid, 
            subject="HooHacks Spot Confirmed!", 
            message=settings.CONFIRMED_EMAIL.format(u.application.full_name),
            action="confirmed",
            sent=tz.localize(datetime.now()),
            redirect_url="/dashboard",
            user=u
        )
        e.send_email()
        print(e.uuid_confirmation)

        return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "msg": "Your confirmation application has been submitted!", 
                "allow": ALLOW
            })
            