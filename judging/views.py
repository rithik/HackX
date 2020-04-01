from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

import uuid
from pytz import timezone
from datetime import datetime
from applications.models import Application, Confirmation
from users.models import User, EmailView, Ticket
from administration.models import Settings
from .models import Organization, Team, Category, Demo
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import dropbox 
import re
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO
from math import sqrt
from queue import PriorityQueue
import heapq
import random
import math
from collections import deque
from itertools import chain

@login_required
def make_judge_manual(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if request.method == "GET":
        return render(request, "make-judge.html", {
            "highlight": "", 
            "user": u,
            "msg": "Please enter the judging password to make yourself a judge!",
            "organizations": Organization.objects.all()
        })

    if request.method == "POST":
        judge_password = request.POST.get('judge_password', '')
        first_name = request.POST.get('first-name', '')
        last_name = request.POST.get('last-name', '')
        org_id = request.POST.get('organization-id', 0)
        if judge_password == settings.JUDGING_PASSWORD:
            u.is_judge = True
            u.first_name = first_name
            u.last_name = last_name
            o = Organization.objects.get(id=org_id)
            u.organization = o
            u.save()
            return render(request, "make-judge.html", {
                "highlight": "", 
                "user": u,
                "msg": "You are now a judge!",
                "organizations": Organization.objects.all()
            })
        else:
            return render(request, "make-judge.html", {
                "highlight": "", 
                "user": u,
                "msg": "Incorrect Password! Try again!",
                "organizations": Organization.objects.all()
            })     

@login_required
def import_categories_from_devpost(request):
    u = request.user
    if not u.is_authenticated:
        return JsonResponse({
            "message": "Not logged in",
            "code": "403"
        })
    if not u.is_admin:
        return JsonResponse({
            "message": "You are not an admin! You cannot perform this action!",
            "code": "403"
        })

    if request.method == 'GET':
        context = {
            'categories': Category.objects.all().order_by('name'),
            'organizations': Organization.objects.all(),
            "jadminHighlight" : "categories",
            "highlight": "judging-admin"
        }
        return render(request, 'edit_categories_list.html', context)
    elif request.method == 'POST':
        devpost_url = request.POST.get('devpost_url', '')
        if devpost_url == "":
            return JsonResponse({
                "message": "Invalid URL",
                "code": "404"
            })

        # Get devpost data
        r = requests.get(devpost_url)
        if r.status_code != 200:
            return JsonResponse({
                "message": 'Bad URL, Response <{}>'.format(r.status_code),
                "code": "404"
            })

        soup = BeautifulSoup(r.text, 'html.parser')

        # Scrape prize information
        prize_list_items = soup.find_all('div', attrs={'class': 'prize'})
        raw_prize_texts = []
        for prize_li in prize_list_items:
            raw_prize_texts.append(prize_li.find('h6').text.strip())

        # Extract name and number of winners
        # Example: "Best Overall Hack   (2)"
        pattern = re.compile('\(\d+\)$')
        prizes = []
        for raw_text in raw_prize_texts:
            pattern_match = pattern.search(raw_text)
            if pattern_match:
                start_index = pattern_match.span()[0]
                prizes.append({
                    'name': raw_text[:start_index].strip(),
                    'num_winners': int(pattern_match.group()[1:-1])
                })
            else:
                prizes.append({
                    'name': raw_text,
                    'num_winners': 1
                })

        # Actually create prizes if they don't exist
        created_categories = []
        organizers = Organization.objects.get(name="Organizers")
        for prize in prizes:
            if len(Category.objects.filter(name=prize['name'])) > 0:
                continue

            Category.objects.create(name=prize['name'],
                            organization_id=organizers.id,
                            number_winners=prize['num_winners'])
        return redirect('import_categories_from_devpost')
    return redirect('import_categories_from_devpost')

@login_required
def edit_categories(request):
    u = request.user
    if not u.is_authenticated:
        return JsonResponse({
            "message": "Not logged in",
            "code": "403"
        })
    if not u.is_admin:
        return JsonResponse({
            "message": "You are not an admin! You cannot perform this action!",
            "code": "403"
        })
    if request.method == "POST":
        update = request.POST.get('update', '')
        if update == "true":
            update = True
        else:
            update = False

        delete = request.POST.get('delete', '')
        if delete == "true":
            delete = True
        else:
            delete = False

        add = request.POST.get('add', '')
        if add == "true":
            add = True
        else:
            add = False

        if add:
            name = request.POST.get('name', '')
            org = request.POST.get('org', '')
            winning = request.POST.get('winning', 1)
            judges = request.POST.get('judges', 1)
            opt_in = request.POST.get('opt_in', False)

            if opt_in == "true":
                opt_in = True
            else:
                opt_in = False

            c = Category.objects.create(
                name=name,
                organization=Organization.objects.get(id=org),
                number_winners=int(winning),
                min_judges=int(judges),
                is_opt_in=opt_in
            )
            return JsonResponse({
                "message": "success",
                "cid": c.id
            })
    
        if update:
            cid = request.POST.get('cid', '')
            name = request.POST.get('name', '')
            org = request.POST.get('org', '')
            winning = request.POST.get('winning', 1)
            judges = request.POST.get('judges', 1)
            opt_in = request.POST.get('opt_in', False)

            if opt_in == "true":
                opt_in = True
            else:
                opt_in = False

            c = Category.objects.get(id=cid)
            c.name = name
            c.organization = Organization.objects.get(id=org)
            c.number_winners = int(winning)
            c.min_judges = int(judges)
            c.is_opt_in = opt_in
            c.save()
            return JsonResponse({
                "message": "success",
                "category": c.name
            })

        if delete:
            cid = request.POST.get('cid', '')
            c = Category.objects.get(id=cid)
            c.delete()
            return JsonResponse({
                "message": "success",
                "category": "deleted"
            })


    return JsonResponse({
        "message": "Must be a POST"
    })

@login_required
def import_teams_from_devpost(request):
    """Import teams from devpost submissions data export.

    The team names, submission URLs, and opt-in prize categories are captured.
    Unlike other POST-REDIRECT-GET-RERENDER handlers, this function will fully
    redirect to the edit teams page, causing a full refresh. The reason for this
    is handling file uploads with ajax is rather annoying.
    """
    if not request.user.is_admin:
        return JsonResponse({
            "error": "Must be admin"
        })

    if request.method == 'GET':
        return redirect('edit_teams')

    elif request.method == 'POST':
        context = {}
        # source: https://www.pythoncircle.com/post/30/how-to-upload-and-process-the-csv-file-in-django/
        csv_file = request.FILES.get('devpost_csv', None)
        # check is a csv file
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({
                "error": "Uploaded file must be a .csv"
            })

        # check if file too large
        if csv_file.multiple_chunks():
            return JsonResponse({
                "error": 'Uh oh, file ({:.2f}MB) too large, max (2.5MB)'.format(
                csv_file.size / (1000 * 1000))
            })
        
        organizers = Organization.objects.get(name="Organizers")
        data = csv_file.read().decode("utf-8")
        reader = csv.reader(StringIO(data), csv.excel)
        headers = next(reader)
        num_teams_created = 0
        for row in reader:
            prize = row[0]
            project_name = row[1]
            project_url = row[2]
            # get or create team
            teams = Team.objects.filter(link=project_url)
            if len(teams) == 0:
                num_teams_created += 1
                team = Team.objects.create(name=project_name, link=project_url)
            else:
                team = teams[0]

            if prize != '':
                # get or create category
                categories = Category.objects.filter(name=prize)
                if len(categories) == 0:
                    category = Category.objects.create(
                        name=prize, organization_id=organizers.id, is_opt_in=True)
                    #messages.warning(request, '"{}" was created and assigned to "{}" by default'.format(
                        #prize, organizers.name))
                else:
                    # TODO: more robust edge case checking
                    category = categories[0]

                # add team to category
                category.submissions.add(team)
        #messages.info(request, '{} new teams created'.format(num_teams_created), extra_tags='import_teams_from_devpost')
        return redirect('import_teams_from_devpost')
    return redirect('import_teams_from_devpost')

@login_required
def edit_teams(request):
    """Page for editing teams."""
    if not request.user.is_admin:
        return redirect('/')

    if request.method == 'GET':
        context = {
            'teams': Team.objects.filter(is_anchor=False).order_by('table', 'name'),
            "jadminHighlight" : "teams",
            "highlight": "judging-admin"
        }
        return render(request, 'edit_teams.html', context)

    return redirect('edit_teams')

@login_required
def update_team(request):
    """Update team information.
    
    Update the team's table and return information about
    if it succeeded and if the new table was different
    from the old table.
    """
    response = {
        'success': False,
        'reason': '',
        'message': ''
    }
    if not request.user.is_admin:
        response['reason'] = 'Must be admin'
        return JsonResponse(response)

    if request.method != 'POST':
        response['reason'] = 'Must be POST request'
        return JsonResponse(response)

    tid = request.POST.get('tid', -1)
    team = Team.objects.filter(id=tid)[0]

    if request.POST.get('delete', False):
        team.delete()
        response['success'] = True
        response['message'] = 'success'
        return JsonResponse(response)

    elif request.POST.get('update', True):
        table = request.POST.get('table', '0')
        name = request.POST.get('name', '')
        team.table = table
        team.name = name
        team.save()
        response['success'] = True
        response['message'] = 'success'
        return JsonResponse(response)
    
    return JsonResponse

@login_required
def assign_tables(request):
    """Assign tables to teams.

    Only staff can assign teams.
    """
    if not request.user.is_admin:
        return JsonResponse({
            "message": "Not authorized"
        })

    if request.method == 'GET':
        teams = Team.objects.all().order_by('id')
        num_digits = len(str(len(teams)))
        table_cnt = 1
        for team in teams:
            zeros_needed = num_digits - len(str(table_cnt))
            table_number = zeros_needed * '0' + str(table_cnt)
            team.table = table_number
            team.save()
            table_cnt += 1
        return redirect('edit_teams')
    return redirect('edit_teams')

@login_required
def assign_demos(request):
    """Assign demos to judges.

    Only staff can assign demos.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'reason': 'Must be admin'})

    if request.method != 'GET':
        return JsonResponse({'success': False, 'reason': 'Must be GET'})

    teams = Team.objects.all()
    judges = User.objects.filter(is_judge=True)

    for k in Demo.objects.all():
        if not k.completed:
            k.delete()

    # ensure everyone is signed up for non-opt-in prizes
    non_opt_in_categories = Category.objects.filter(is_opt_in=False)
    for team in teams:
        for category in non_opt_in_categories:
            category.submissions.add(team)

    # first, assign teams to sponsor prizes
    # TODO: currently does not guarantee min_judges
    organizers = Organization.objects.get(name="Organizers")
    for category in Category.objects.all():
        if category.organization.id == organizers.id:  # skip organizer categories
            continue
        for team in category.submissions.all():
            judges_for_category = [j for j in judges if j.organization.id == category.organization.id]
            for judge in judges_for_category:
                if len(Demo.objects.filter(team=team, judge=judge).all()) == 0:
                    Demo.objects.create(judge=judge, team=team)
    judge = User.objects.get(email="rithik@gmail.com")
    demos = Demo.objects.filter(judge=judge)

    # # second, assign teams to non-sponsor prizes
    # # priority queue for teams (priority = number of demos already assigned)
    # # priority queue for judges (priority = number of demos already assigned)
    demos_left = {}
    team_q = []
    for team in teams:
        demos = Demo.objects.filter(team=team)
        priority = len(demos)

        for category in Category.objects.all():
            if category.is_opt_in == False:
                if team.id not in demos_left:
                    demos_left[team.id] = {}
                if priority < 1:
                    demos_left[team.id][category.id] = 2
                else:
                    demos_left[team.id][category.id] = category.min_judges
        heapq.heappush(team_q, (priority, team.id))

    judge_q = []
    for judge in judges:
        demos = Demo.objects.filter(judge=judge)
        priority = len(demos)
        heapq.heappush(judge_q, (priority, judge.id))
    

    while not len(team_q) == 0:
        team_priority, team_id = heapq.heappop(team_q)

        if not any(demos_left[team_id].values()):  # if no more demos needed
            continue

        for category_id, num_needed in demos_left[team_id].items():
            if num_needed == 0:
                continue
            team_priority += 1
            demos_left[team_id][category_id] -= 1
            judge_priority, judge_id = heapq.heappop(judge_q)
            judge_priority += 1
            heapq.heappush(judge_q, (judge_priority, judge_id))
            team = Team.objects.get(id=team_id)
            judge = User.objects.get(id=judge_id)
            if len(Demo.objects.filter(team=team, judge=judge)) == 0:
                Demo.objects.create(judge=judge, team=team)
            break

        heapq.heappush(team_q, (team_priority, team_id))

    return redirect('team_progress')

@login_required
def team_progress(request):
    """Page for getting team progress.
    """
    if not request.user.is_admin:
        return redirect('.')

    if request.method == 'GET':
        all_judges = User.objects.filter(is_judge=True)
        judges = []
        for judge in all_judges:
            judge_demos = Demo.objects.filter(judge=judge)
            num_judges_completed = 0
            total = 0
            for demo in judge_demos:
                if demo.completed:
                    num_judges_completed += 1
                total +=1
            judges.append({
                'name': judge.full_name,
                'num_judges_completed': num_judges_completed,
                'total': total
            })

        all_teams = Team.objects.all().order_by('name')
        total_completed = 0
        total_reqd = 0
        num_judges_completed = 0
        total = 0
        teams = []
        all_anchor_teams = Team.objects.filter(is_anchor=True)
        all_nonanchor_teams = Team.objects.filter(is_anchor=False)
        for team in all_anchor_teams:
            team_demos = Demo.objects.filter(team=team)
            num_judges_completed = 0
            total = 0
            for demo in team_demos:
                if demo.completed:
                    num_judges_completed += 1
                    total_completed += 1
                total +=1
                total_reqd += 1
            teams.append({
                'name': team.name,
                'id': team.id,
                'table': team.table,
                'num_judges_completed': num_judges_completed,
                'total': total
            })
        for team in all_nonanchor_teams:
            team_demos = Demo.objects.filter(team_id=team.id)
            num_judges_completed = 0
            total = 0
            for demo in team_demos:
                if demo.completed:
                    num_judges_completed += 1
                    total_completed += 1
                total +=1
                total_reqd += 1
            teams.append({
                'name': team.name,
                'id': team.id,
                'table': team.table,
                'num_judges_completed': num_judges_completed,
                'total': total
            })

        teams.insert(0, {
            'name': 'ALL TEAMS',
            'id': '-1',
            'table': 'ALL',
            'num_judges_completed': total_completed,
            'total': total_reqd
        })

        context = {
            'teams': teams,
            'judges': judges,
            'num_judges': len(User.objects.filter(is_judge=True)),
            "jadminHighlight" : "team-progress",
            "highlight": "judging-admin"
        }
        return render(request, 'team_progress.html', context)
    return redirect('team_progress')

@login_required
def judging_queue(request):
    """Demo queue for judges.

    If not logged in, redirects to index. If logged in, but the
    profile is incomplete, redirect to profile. If logged in and
    the profile is complete, render page.
    """
    if not request.user.is_judge:
        return redirect('/')
        
    if request.method == 'GET':
        demos = Demo.objects.filter(judge=request.user, team__is_anchor=False).order_by('team__table')
        demos = sorted(demos, key=lambda d: d.is_for_judge_category, reverse=True)
        demo_queue = []
        past_demos = []
        for demo in demos:
            if demo.completed:
                past_demos.append(demo)
            else:
                demo_queue.append(demo)

        # This ensures that all of the judges do not start judging with the teams with the lower table numbers
        demo_queue_rotated = deque(demo_queue)
        if len(demo_queue) == 0:
            rotate_amt = 0
        else:
            rotate_amt = hash(request.user) % (len(demo_queue))
        demo_queue_rotated.rotate(rotate_amt)

        normalization_demos = Demo.objects.filter(judge=request.user, team__is_anchor=True).order_by('team__table')
        for d in normalization_demos:
            demo_queue_rotated.insert(0, d)

        demo_queue_data = []
        for d in demo_queue_rotated:
            demo_queue_data.append({
                "demo": d,
                "team": d.team,
                "categories": d.team.categories.all()
            })

        past_demo_data = []
        for d in past_demos:
            past_demo_data.append({
                "demo": d,
                "team": d.team,
                "categories": d.team.categories.all()
            })

        context = {
            'user': request.user,
            'demo_queue': demo_queue_data,
            'past_demos': past_demo_data,
            'highlight': 'judging'
        }
        return render(request, 'queue.html', context)
    return redirect('queue')

@login_required
def evaluate(request):
    """Form judges use to evaluate submissions.

    If not logged in, redirects to index. If logged in, but the
    profile is incomplete, redirect to profile. Otherwise, render
    the page. However, if judging has not started, disallow any
    form submissions.
    """
    if not request.user.is_judge:
        return redirect('/')

    if request.method == 'GET':
        context = {
            "all_teams": Team.objects.all()
        }
        if request.GET.get('team'):
            # Get team, if specified
            team_id = request.GET.get('team')
            teams = Team.objects.filter(id=team_id)
            if len(teams) > 0:
                team = teams[0]

                # Get any initial data
                demos = Demo.objects.filter(judge=request.user, team=team)
                remaining_demos = Demo.objects.filter(judge=request.user, completed=False).count()
                time_remaining = Settings.objects.all()[0].judging_deadline - datetime.now().astimezone(settings.TZ)
                minutes_left = (int) (time_remaining.total_seconds() / 60.0)
                time_per_presentation = (int) ((minutes_left - (remaining_demos * 1)) / remaining_demos)
                if time_per_presentation < 0:
                    time_per_presentation = 0

                demo = demos

                if len(demos) > 0:
                    demo = demos[0]

                no_table_teams = Team.objects.filter(table="").all().order_by('name')
                table_teams = Team.objects.exclude(table="").all()

                all_teams = chain(table_teams, no_table_teams)

                context = {
                    "demo": demo,
                    "all_teams": all_teams,
                    "remaining_demos": remaining_demos,
                    "time_per_presentation": time_per_presentation,
                    'highlight': 'judging'
                }

        return render(request, 'evaluate.html', context)

    elif request.method == 'POST':
        if len(User.objects.filter(id=request.user.id, is_judge=True)) == 0:
            return JsonResponse({
                "message": "You are not a judge!"
            })

        # Get or create demo
        judge_id = request.user.id
        team_id = request.POST.get('team')
        team = Team.objects.get(id=team_id)
        demos = Demo.objects.filter(judge=request.user, team=team)
        
        if len(demos) > 0:
            demo = demos[0]
        else:
            demo = Demo.objects.create(judge=request.user, team=team)

        ui = request.POST.get('ui', 0)
        creativity = request.POST.get('creativity', 0)
        functionality = request.POST.get('functionality', 0)
        impact = request.POST.get('impact', 0)
        feasibility = request.POST.get('feasibility', 0)

        demo.ui = int(ui)
        demo.creativity = int(creativity)
        demo.functionality = int(functionality)
        demo.impact = int(impact)
        demo.feasibility = int(feasibility)
        demo.completed = True
        demo.raw_score = int(ui) + int(creativity) + int(functionality) + int(impact) + int(feasibility)
        demo.save()

        return redirect('judging_queue')

@login_required
def get_team_categories(request):
    if request.method == "GET":
        team_id = request.GET.get('team_id', -1)
        if team_id == -1:
            return JsonResponse({
                "Error": "Could not get Team Categories - invalid team id"
            })
        t = Team.objects.get(id=int(team_id))
        
        return JsonResponse({
            "categories": [category.name for category in t.categories.all()]
        })

    return JsonResponse({
        "Error": "Not a GET request"
    })

@login_required
def scores(request):
    # TODO: move computation into POST request
    """Page for viewing and normalizing scores."""
    if not request.user.is_admin:
        return redirect('index')

    if request.method == 'GET':
        context = {}

        teams = Team.objects.all()
        team_scores = []
        for team in teams:
            team_demos = Demo.objects.filter(team=team)
            demo_raw_totals = []
            demo_norm_totals = []
            for demo in team_demos:
                demo_raw_totals.append(demo.raw_score)
                demo_norm_totals.append(demo.norm_score)
            try:
                team_raw_score = sum(demo_raw_totals) / len(demo_raw_totals)
                team_norm_score = sum(demo_norm_totals) / len(demo_norm_totals)
            except:
                team_raw_score = 0
                team_norm_score = 0
            if team_norm_score == 0:
                team_norm_score = team_raw_score
            team_scores.append((team_norm_score, team_raw_score, team))

        rankings = sorted(team_scores, key=lambda i: i[0], reverse=True)
        ranks = []
        count = 0
        for k in rankings:
            count += 1
            categories = [category.name for category in k[2].categories.all()]
            print(categories)
            ranks.append({
                'norm_score': math.floor(k[0] * 1000) / 1000,
                'raw_score': math.floor(k[1] * 1000) / 1000,
                'team': k[2].name,
                'ranking': count,
                'id': k[2].id,
                'categories': categories
            })
        
        # norm_score, raw_score, winner = rankings[0]
        # # winning_scores = []
        # for demo in Demo.objects.filter(team=winner):
        #     score = demo.raw_score
        #     winning_scores.append([score.value for score in scores])

        context['rankings'] = ranks
        context['jadminHighlight'] = "scores"
        context['highlight'] = "judging-admin"
        return render(request, 'scores.html', context)
    return redirect('scores')

@login_required
def normalize_scores(request):
    response = {
        'success': False,
        'reason': ''
    }

    if request.method == 'GET':
        ### Calculate judge standard deviation offsets
        anchor_teams = Team.objects.filter(is_anchor=True)
        if len(anchor_teams) == 0:
            response['reason'] = 'No anchor teams to normalize on'
            return JsonResponse(response)

        judges = User.objects.filter(is_judge=True)

        # Compute means and standard deviations
        anchor_means = {}
        anchor_sds = {}
        all_anchor_mean = 0
        anchor_sd_mean = 0
        for team in anchor_teams:
            team_scores = [demo.raw_score for demo in Demo.objects.filter(team=team)]
            scores_mean = sum(team_scores) / len(team_scores)
            scores_var = sum([pow(score - scores_mean, 2) for score in team_scores]) / len(team_scores)
            scores_sd = sqrt(scores_var)
            anchor_means[team.id] = scores_mean
            anchor_sds[team.id] = scores_sd


        # Compute judge sd offsets
        for judge in judges:
            offsets = []
            for team in anchor_teams:
                demos = Demo.objects.filter(judge=judge, team=team)
                if len(demos) != 0:
                    offsets.append((demos[0].raw_score - anchor_means[team.id]))
                    # Could also divide this by anchor_sds[team.id] to get the zscore
                    # For simplicity, let's assume the distribution of scores doesn't change
                    #   for each team, an arguably-reasonable assumption
            if len(offsets) > 0:
                judge.sd_offset = sum(offsets) / len(offsets)
                judge.save()
                
        # Compute demo norm_scores
        for demo in Demo.objects.all():
            if demo.team.is_anchor:
                continue
            demo.norm_score = demo.raw_score - demo.judge.sd_offset
            demo.save()
        response['success'] = True
        return redirect('scores')
    return JsonResponse(response)

@login_required
def assign_anchor_to_judges(request):
    if not request.user.is_admin:
        return HttpResponse('Must be admin')

    if request.method == 'GET':
        return JsonResponse({
            'message': 'error',
            'error': 'Must be POST request'
        })
    elif request.method == 'POST':
        team_id = request.POST.get('team_id', None)
        if team_id:
            judges = User.objects.filter(is_judge=True)
            team = Team.objects.filter(id=team_id)[0]
            for judge in judges:
                if len(Demo.objects.filter(team=team, judge=judge).all()) == 0:
                    Demo.objects.create(judge=judge, team=team)
        return JsonResponse({
            'message': 'success'
        })

@login_required
def normalize_teams(request):
    if not request.user.is_admin:
        return HttpResponse('Must be admin')
    if request.method == 'GET':
        context = {
            'teams': Team.objects.filter(is_anchor=True)
        }
        context['jadminHighlight'] = "normalization"
        context['highlight'] = "judging-admin"
        return render(request, 'normalize_teams.html', context)
    if request.method == "POST":
        add = request.POST.get('add', False)
        if add == "true":
            team = Team.objects.create(name='Normalization Session {}'.format(str(uuid.uuid1())), link='', is_anchor=True)
            return redirect('normalize_teams')
        delete = request.POST.get('delete', False)
        if delete == "true":
            team_id = request.POST.get('team_id', None)
            team = Team.objects.get(id=team_id)
            team.delete()
            return JsonResponse({
                "message": 'success'
            })

@login_required
def simulate_demos(request):
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
        for demo in Demo.objects.all():
            demo.ui = random.randint(1, 5)
            demo.creativity = random.randint(1, 5)
            demo.functionality = random.randint(1, 5)
            demo.impact = random.randint(1, 5)
            demo.feasibility = random.randint(1, 5)
            demo.completed = True
            demo.save()
            demo.raw_score = demo.ui + demo.creativity + demo.functionality + demo.impact + demo.feasibility
            demo.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
