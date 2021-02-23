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
from .models import Application, Confirmation, TshirtOrder
from users.models import User, EmailView
import dropbox 
from administration.models import Settings
from administration import nametag
import base64 

dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

@login_required
def application(request, msg=''):
    ALLOW = True
    tz = timezone('US/Eastern')
    if datetime.now().timestamp() >=  Settings.objects.all()[0].application_submission_deadline.timestamp():
        ALLOW = False
    u = request.user
    a = u.application
    if not request.user.is_authenticated:
        return redirect("/logout")
    if not request.method == "POST":
        if msg == 'saved':
            msg = 'Your application has been submitted!'
        else:
            msg = ''
        return render(request, "application.html", {
            "user": u, 
            "app": a,
            "schools": settings.SCHOOLS, 
            "genders": settings.GENDERS,
            "races": settings.RACES, 
            "grad_year": settings.GRADUATION_YEARS,
            "highlight": "application",
            "travel_methods": settings.TRAVEL_METHODS, 
            "msg": msg, 
            "allow": ALLOW
        })
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')

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

        first_name = request.POST.get('first-name', '')
        last_name = request.POST.get('last-name', '')
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
        mlh_consent = request.POST.get('mlh-consent', '')
        referrer = request.POST.get('referrer', '')

        a.first_name = first_name
        a.last_name = last_name
        a.birthday = birthday
        a.school = school if school != "Other" else "Other - Other"
        a.grad_year = grad_year
        a.gender = gender
        a.race = race
        a.describe = describe
        a.major = major
        a.hackathons = hackathons
        a.why = why
        
        friends = User.objects.filter(email=base64.b64decode(referrer).decode("utf-8", "ignore"))
        if friends.count() == 1 and friends.first() != u and not a.referrer_locked:
            a.referrer = referrer
            a.referrer_locked = True
            friend = friends.first()
            friend.raffle_tickets += 1
            friend.save()

        if mlh == "on":
            a.mlh_rules = True
        else:
            a.mlh_rules = False

        if mlh_consent == "on":
            a.mlh_consent = True
        else:
            a.mlh_consent = False

        a.app_complete = True
        u.first_name = first_name
        u.last_name = last_name
        
        u.save()
        a.save()
        
        return redirect(application, msg='saved')
        # render(request, "application.html", {
        #     "user": u, 
        #     "app": a,
        #     "schools": settings.SCHOOLS, 
        #     "genders": settings.GENDERS,
        #     "races": settings.RACES, 
        #     "grad_year": settings.GRADUATION_YEARS,
        #     "highlight": "application",
        #     "travel_methods": settings.TRAVEL_METHODS, 
        #     "msg": "Your application has been submitted!", 
        #     "allow": ALLOW
        # })

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
    if datetime.now().timestamp() >= Settings.objects.all()[0].application_confirmation_deadline.timestamp():
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
            "allow": ALLOW,
            "all_carriers": list(settings.CARRIER_EMAIL_LOOKUP)
        })
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')
        if button_type == "decline":
            c.declined = True
            c.confirmed = False
            c.save()
            conf_deadline = Settings.objects.all()[0].application_confirmation_deadline_fmt()
            return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "declined": True,
                "msg": "We're sorry that you can't make it to {}. You can still confirm your spot until the confirmation deadline ({}).".format(settings.EVENT_NAME, conf_deadline), 
                "allow": ALLOW,
                "all_carriers": list(settings.CARRIER_EMAIL_LOOKUP)
            })
            
        tshirt = request.POST.get('tshirt', '')
        dietary = request.POST.get('dietary', '')
        phone = request.POST.get('phone', '')
        carrier = request.POST.get('carrier', 'Other')
        github = request.POST.get('github', '')
        notes = request.POST.get('notes', '')
        school = request.POST.get('school', '')
        discord_id = request.POST.get('discord', '')
        file = request.FILES['file']
        if file == '':
            return render(request, "confirmation.html", {
                "user": u, 
                "app": a, 
                "c": c, 
                "highlight": "confirmation",
                "tshirt_sizes": settings.TSHIRT_SIZES, 
                "dietary_restrictions": settings.DIETARY_RESTRICTIONS,
                "declined": False,
                "msg": "", 
                "allow": ALLOW,
                "all_carriers": list(settings.CARRIER_EMAIL_LOOKUP)
            })

        file_path = ""
        if file:
            curr_year = Settings.objects.all()[0].application_confirmation_deadline.year
            file_path = '/Resumes-' + str(curr_year) +  '/' + str(a.grad_year) + '/' + u.full_name + "-" + str(u.qr_hash) + '-Resume.pdf'
            if not c.resume_file_name == "":
                try:
                    dbx.files_delete_v2(file_path)
                except:
                    print("can't delete")
            try:
                dbx.files_upload(file.file.read(), file_path)
            except:
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
                "declined": False,
                "msg": "", 
                "allow": ALLOW,
                "all_carriers": list(settings.CARRIER_EMAIL_LOOKUP)
            })

        c.resume_file_name = file_path
        c.tshirt = tshirt
        c.dietary = dietary
        c.phone = phone
        c.carrier = carrier
        c.github = github
        c.notes = notes
        c.discord_id = discord_id
        c.confirmed = True
        c.declined = False
        c.save()
        if school != "":
            a.school = "Other - {}".format(school)
            a.save()

        try:
            nametag.make_image(u.first_name, u.last_name, u.qr_hash)
        except:
            file_path = '/Nametags/' + u.first_name + " " + u.last_name + "-" + str(u.qr_hash) + '.png'
            dbx.files_delete_v2(file_path)
            nametag.make_image(u.first_name, u.last_name, u.qr_hash)

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
                "declined": False,
                "allow": ALLOW,
                "all_carriers": list(settings.CARRIER_EMAIL_LOOKUP)
            })

@login_required
def order_tshirt(request):
    user = request.user
    a = user.application
    c = user.confirmation
    if not a.accepted:
        return render(request, "tshirtshipping.html", {
            "user": user, 
            "highlight": "order-tshirt",
            "tshirt_sizes": settings.TSHIRT_SIZES, 
            "msg": "", 
            "error": "Unfortunately, you cannot order a t-shirt! You did not confirm your registration in time."
        })

    if not c.confirmed:
        return render(request, "tshirtshipping.html", {
            "user": user, 
            "highlight": "order-tshirt",
            "tshirt_sizes": settings.TSHIRT_SIZES, 
            "msg": "", 
            "error": "Unfortunately, you cannot order a t-shirt! You did not confirm your registration in time."
        })

    if request.method == "POST":
        t = TshirtOrder.objects.get(user=request.user)
        size = request.POST.get('size', '')
        street_address = request.POST.get('street-address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')
        zip_code = request.POST.get('zip-code', '')
        devpost_url = request.POST.get('devpost-url', '')
        devpost_email = request.POST.get('devpost-email', '')

        t.tshirt = size
        t.street_address = street_address
        t.city = city
        t.state = state
        t.country = country
        t.zip_code = zip_code
        t.devpost_url = devpost_url
        t.devpost_email = devpost_email
        t.save()

        return render(request, "tshirtshipping.html", {
            "user": user, 
            "highlight": "order-tshirt",
            "tshirt_sizes": settings.TSHIRT_SIZES, 
            "msg": "Your T-Shirt order has been placed! Due to the COVID-19 situation, it may take a few weeks for your t-shirt to actually ship to you.", 
            "error": "",
            "size": t.tshirt,
            "street_address": t.street_address,
            "city": t.city,
            "state": t.state, 
            "country": t.country,
            "zip_code": t.zip_code,
            "devpost_url": t.devpost_url,
            "devpost_email": t.devpost_email
        })

    t = TshirtOrder.objects.filter(user=request.user).count()
    if t == 0: 
        t = TshirtOrder.objects.create(user=request.user)
    else:
        t = TshirtOrder.objects.get(user=request.user)
    return render(request, "tshirtshipping.html", {
        "user": user, 
        "highlight": "order-tshirt",
        "tshirt_sizes": settings.TSHIRT_SIZES, 
        "msg": "", 
        "error": "",
        "size": t.tshirt,
        "street_address": t.street_address,
        "city": t.city, 
        "state": t.state, 
        "country": t.country,
        "zip_code": t.zip_code,
        "devpost_url": t.devpost_url,
        "devpost_email": t.devpost_email
    })
