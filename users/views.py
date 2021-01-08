from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

from datetime import datetime
from pytz import timezone
import uuid
from .models import User, EmailView, HackerTeam
from applications.models import Application, Confirmation
from administration.models import Settings
from judging.models import Organization


def redirect_dashboard(request):
    return redirect('/dashboard')


def setup(request):
    if len(Settings.objects.all()) == 0:
        tz = settings.TZ
        Settings.objects.create(
            application_submission_deadline=datetime.now(),
            application_confirmation_deadline=datetime.now(),
            judging_deadline=datetime.now()
        )
        o = Organization.objects.create(name="Organizers")
        o = Organization.objects.create(name="Other")
    return redirect('/')


@login_required
def dashboard(request):
    u = request.user
    a = u.application
    if not request.user.is_authenticated:
        return redirect("/logout")
    c = u.confirmation
    confirmation = True
    if a.accepted == False:
        confirmation = False
    else:
        if c.confirmed:
            confirmation = "accepted"
        if c.declined:
            confirmation = "rejected"
    try:
        context = {
            "user": u,
            "app": a,
            "highlight": "dashboard",
            "submission_deadline": Settings.objects.all()[0].application_submission_deadline_fmt(),
            "confirmation": confirmation,
            "confirmation_deadline": Settings.objects.all()[0].application_confirmation_deadline_fmt(),
        }
    except IndexError:
        return redirect('setup')
    return render(request, "dashboard.html", context)


@login_required
def view_teams(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    if u.application.app_complete == False:
        context = {
            "user": u,
            "highlight": "team",
            "team": None,
            "allowed": False
        }
        return render(request, "teams.html", context)

    context = None
    if request.method == "GET":
        context = {
            "user": u,
            "highlight": "team",
            "team": u.team if u.team else None,
            "msg": "",
            "allowed": True
        }
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')
        if button_type == "join":
            try:
                team_id = request.POST.get('team-id', '')
                t = HackerTeam.objects.get(unique_code=team_id)
                u.team = t
                u.save()
                context = {
                    "user": u,
                    "highlight": "team",
                    "team": u.team if u.team else None,
                    "msg": "Added to Team",
                    "error": False,
                    "section": "join",
                    "allowed": True
                }
            except:
                context = {
                    "user": u,
                    "highlight": "team",
                    "team": u.team if u.team else None,
                    "msg": "Invalid Team ID entered",
                    "error": True,
                    "section": "join",
                    "allowed": True
                }
        elif button_type == "create":
            team_name = request.POST.get('team-name', '')
            t = HackerTeam.objects.create(name=team_name)
            u.team = t
            u.save()
            context = {
                "user": u,
                "highlight": "team",
                "team": u.team if u.team else None,
                "msg": "Created New Team",
                "error": False,
                "section": "create",
                "allowed": True
            }
        elif button_type == "leave":
            u.team = None
            u.save()
            context = {
                "user": u,
                "highlight": "team",
                "team": u.team if u.team else None,
                "msg": "Left Team",
                "error": False,
                "section": "join",
                "allowed": True
            }
        elif button_type == "delete":
            u.team.delete()
            context = {
                "user": u,
                "highlight": "team",
                "team": None,
                "msg": "Team Deleted",
                "error": False,
                "section": "join",
                "allowed": True
            }
    if context == None:
        context = {
            "user": u,
            "highlight": "team",
            "team": u.team if u.team else None,
            "msg": "Invalid request",
            "error": True,
            "section": "join",
            "allowed": True
        }
    return render(request, "teams.html", context)


def login_page(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/dashboard")
        else:
            return render(request, "login_page.html", {"message": "None"})
    else:
        if request.POST.get('button-type') == "register":
            email = request.POST.get('email', '')
            f = User.objects.filter(email=email)
            if not f.count() == 0:
                return render(request, "login_page.html", {"message": "There is already an account found with this email address!"})

            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            u = User.objects.filter(email=email)
            if len(u) != 0:
                return redirect('index')

            u = User.objects.create(
                username=email, email=email, password=password, verified=False)
            u.set_password(password)
            u.save()

            a = Application.objects.create(user=u)
            c = Confirmation.objects.create(user=u)
            tz = timezone('US/Eastern')
            email_uuid = uuid.uuid1()
            e = EmailView.objects.create(
                uuid_confirmation=email_uuid,
                subject="HooHacks Email Verification",
                message=settings.VERIFY_EMAIL.format(
                    u.email, settings.PROD_URL, email_uuid),
                action="verify",
                sent=tz.localize(datetime.now()),
                redirect_url="/users/login/",
                user=u
            )
            e.send_email()
            print(e.uuid_confirmation)
            return render(request, "login_page.html", {"message": "User account created! Please check your email to confirm your account!"})
        elif request.POST.get('button-type') == "login":
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            u = User.objects.filter(email__iexact=email)
            if u.count() == 0:
                return render(request, "login_page.html", {"message": "No account found with this email address!"})
            u = u.first()
            user = authenticate(
                request, username=u.username, password=password)
            if user is not None:
                if not u.verified:
                    return render(request, "login_page.html", {"message": "Your account was not verified! Please check your email (and spam folder) to confirm your account!"})
                login(request, user)
                next_url = request.GET.get('next', '/dashboard')
                return redirect(next_url)
            return render(request, "login_page.html", {"message": "Incorrect Password!"})


def forgot_password(request):
    if request.method == "GET":
        return render(request, "forgot_password.html", {"message": "Please enter your email address to reset your password!", "show": True})
    if request.method == "POST":
        email = request.POST.get('email', '')
        u = User.objects.filter(email=email)
        if u.count() == 0:
            return render(request, "forgot_password.html", {"message": "There is no user associated with that email address!", "show": True})
        u = u.first()
        tz = timezone('US/Eastern')
        email_uuid = uuid.uuid1()
        e = EmailView.objects.create(
            uuid_confirmation=email_uuid,
            subject="HooHacks Password Reset",
            message=settings.PASSWORD_RESET_EMAIL.format(
                u.email, settings.PROD_URL, email_uuid),
            action="reset",
            sent=tz.localize(datetime.now()),
            redirect_url="/reset/{}".format(str(email_uuid)),
            user=u
        )
        e.send_email()
        print(e.uuid_confirmation)
        return render(request, "forgot_password.html", {"message": "Check your email to reset your password!", "show": False})


def reset_password(request, email_uuid):
    if request.method == "GET":
        return render(request, "reset_password.html", {"message": "Please enter a new password!", "show": True, "euuid": email_uuid})
    if request.method == "POST":
        e = EmailView.objects.filter(uuid_confirmation=email_uuid)
        if len(e) == 0:
            return render(request, "reset_password.html", {"message": "This URL is invalid!", "show": False})
        e = e.first()
        u = e.user
        u.set_password(request.POST.get('password', ''))
        u.save()
        return render(request, "reset_password.html", {"message": "Password changed!", "show": False})


def logout_view(request):
    logout(request)
    return redirect("/")
