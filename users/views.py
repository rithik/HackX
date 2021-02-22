from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

from datetime import datetime, timezone as tz
from pytz import timezone
import uuid
from .models import Puzzle, PuzzleSolution, User, EmailView, PuzzleTeam
from applications.models import Application, Confirmation
from administration.models import Settings
from judging.models import Organization
import re
import time
import math

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
        print(u.raffle_id)
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
def view_puzzles(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    if u.application.app_complete == False:
        context = {
            "user": u,
            "highlight": "puzzles",
            "team": None,
            "allowed": False
        }
        return render(request, "puzzles.html", context)

    context = None
    if u.team:
        locked = [solution.puzzle.id for solution in u.team.solutions.all() if solution.locked]
    else:
        locked = []
    if request.method == "GET":
        context = {
            "user": u,
            "highlight": "puzzles",
            "team": u.team if u.team else None,
            "msg": "",
            "allowed": True, 
            "puzzles": Puzzle.objects.all(),
            "locked": locked
        }
    if request.method == "POST":
        button_type = request.POST.get('button-type', '')
        if button_type == "join":
            try:
                team_id = request.POST.get('team-id', '')
                t = PuzzleTeam.objects.get(unique_code=team_id)
                u.team = t
                u.save()
                context = {
                    "user": u,
                    "highlight": "puzzles",
                    "team": u.team if u.team else None,
                    "msg": "Added to Team",
                    "error": False,
                    "section": "join",
                    "allowed": True,
                    "puzzles": Puzzle.objects.all(),
                    "locked": locked
                }
            except:
                context = {
                    "user": u,
                    "highlight": "puzzles",
                    "team": u.team if u.team else None,
                    "msg": "Invalid Team ID entered",
                    "error": True,
                    "section": "join",
                    "allowed": True,
                    "puzzles": Puzzle.objects.all(),
                    "locked": locked
                }
        elif button_type == "create":
            team_name = request.POST.get('team-name', '')
            t = PuzzleTeam.objects.create(name=team_name)
            u.team = t
            u.save()
            context = {
                "user": u,
                "highlight": "puzzles",
                "team": u.team if u.team else None,
                "msg": "Created New Team",
                "error": False,
                "section": "create",
                "allowed": True,
                "puzzles": Puzzle.objects.all(),
                "locked": locked
            }
        elif button_type == "leave":
            if u.team.count() == 1:
                u.team.delete()
            else:
                u.team = None
                u.save()
            context = {
                "user": u,
                "highlight": "puzzles",
                "team": None,
                "msg": "Left Team",
                "error": False,
                "section": "join",
                "allowed": True,
                "puzzles": Puzzle.objects.all(),
                "locked": locked
            }
        elif button_type == "delete":
            u.team.delete()
            context = {
                "user": u,
                "highlight": "puzzles",
                "team": None,
                "msg": "Team Deleted",
                "error": False,
                "section": "join",
                "allowed": True,
                "puzzles": Puzzle.objects.all(),
                "locked": locked
            }
    if context == None:
        context = {
            "user": u,
            "highlight": "puzzles",
            "team": u.team if u.team else None,
            "msg": "Invalid request",
            "error": True,
            "section": "join",
            "allowed": True,
            "puzzles": Puzzle.objects.all(),
            "locked": locked
        }
    return render(request, "puzzles.html", context)

@login_required
def change_puzzle_team_name(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    team = u.team
    team.name = request.POST.get('name', '')
    team.save()
    return JsonResponse({"status": 200, "message": "Success"})

@login_required
def add_puzzle(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    puzzle_text = request.POST.get('text', '')
    puzzle_answer = request.POST.get('answer', '')
    puzzle_points = request.POST.get('points', 0)
    p = Puzzle.objects.create(text=puzzle_text, regex_answer=puzzle_answer, max_points=puzzle_points)
    return JsonResponse({"status": 200, "message": "Success", "pid": p.id})

@login_required
def update_puzzle(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    puzzle_text = request.POST.get('text', '')
    puzzle_answer = request.POST.get('answer', '')
    puzzle_points = request.POST.get('points', 0)
    puzzle_id = request.POST.get('pid', 0)
    p = Puzzle.objects.get(id=puzzle_id)
    p.text = puzzle_text
    p.regex_answer = puzzle_answer
    p.max_points = puzzle_points
    p.save()
    return JsonResponse({"status": 200, "message": "Success", "pid": p.id})

@login_required
def delete_puzzle(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect("/logout")
    puzzle_id = request.POST.get('pid', 0)
    p = Puzzle.objects.get(id=puzzle_id)
    p.delete()
    return JsonResponse({"status": 200, "message": "Success"})

@login_required
def solve_puzzle(request, pid):
    u = request.user
    if not request.user.is_authenticated:
        return redirect('logout')
    p = Puzzle.objects.get(id=int(pid))
    ps = PuzzleSolution.objects.filter(team=u.team, puzzle=p)
    msg = ""
    error = False
    if ps.count() == 0:
        ps = PuzzleSolution.objects.create(team=u.team, puzzle=p, num_attempts=0)
    else:
        ps = ps.first()
    if request.method == "POST":
        user_solution = request.POST.get('solution', '')
        ps.num_attempts += 1
        ps.most_recent_solution = user_solution
        ps.save()

        regex = re.compile(p.regex_answer)
        valid_solution = regex.match(str(user_solution))
        if valid_solution or ps.num_attempts >= 20:
            ps.locked = True
        if valid_solution: 
            confirmation_deadline = Settings.objects.first().application_confirmation_deadline
            num_hours = divmod((datetime.now(tz.utc) - confirmation_deadline).total_seconds(), 3600)[0] 
            points_earned = (math.exp(-0.01 * num_hours + 4.61) - (ps.num_attempts * 3))/100 * p.max_points
            msg = "The code has been cracked! Your team has earned {} points".format(round(points_earned, 4))
            error = False
            ps.points_earned = points_earned
            ps.save()
        else: 
            ps.previous_attempts = "{} submitted by {}\n{}".format(user_solution, u.full_name, ps.previous_attempts)
            ps.save()
            msg = "Sorry, that's not correct. Your team has {} attempts remaining.".format(20 - ps.num_attempts)
            error = True

    context = {
        "user": u,
        "highlight": "puzzles",
        "team": u.team,
        "puzzle": p,
        "solution": ps,
        "msg": msg,
        "error": error
    }
    return render(request, "view_puzzle.html", context)

@login_required
def puzzle_leaderboard(request):
    u = request.user
    if not request.user.is_authenticated:
        return redirect('logout')
    teams_data = []
    all_teams = PuzzleTeam.objects.all()
    for team in all_teams:
        team_data = {
            "id": team.id,
            "name": team.name,
            "member_names": ", ".join(["{} {}".format(member.first_name, member.last_name) for member in team.users.all()]),
            "points_earned": sum([ps.points_earned for ps in team.solutions.all()])
        }
        if team_data["member_names"] != "":
            teams_data.append(team_data)

    teams_data = sorted(teams_data, key=lambda k:k['points_earned'], reverse=True)
    context = {
        "user": u,
        "highlight": "puzzles",
        "teams": teams_data
    }
    return render(request, "puzzle_leaderboard.html", context)

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
            if not settings.REQUIRE_EMAIL_VERIFICATION:
                u.verified = True
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
            if not settings.REQUIRE_EMAIL_VERIFICATION:
                return render(request, "login_page.html", {"message": "User account created! Please log in to fill out your application!"})
            else:
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
