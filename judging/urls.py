"""hoohacks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from . import views 

urlpatterns = [
    path('categories', views.import_categories_from_devpost, name="import_categories_from_devpost"),
    path('categories/update', views.edit_categories, name="edit_categories"),
    path('import/teams', views.import_teams_from_devpost, name='import_teams_from_devpost'),
    path('teams', views.edit_teams, name='edit_teams'),
    path('teams/update', views.update_team, name='update_teams'),
    path('teams/assign_tables', views.assign_tables, name='assign_tables'),
    path('teams/progress', views.team_progress, name='team_progress'),
    path('demos/assign', views.assign_demos, name='assign_demos'),
    path('queue', views.judging_queue, name='judging_queue'),
    path('evaluate', views.evaluate, name='evaluate'),
    path('scores', views.scores, name='scores'),
    path('scores', views.scores, name='scores'),
    path('normalize', views.normalize_teams, name='normalize_teams'),
    path('assign_anchor_to_judges', views.assign_anchor_to_judges, name='assign_anchor_to_judges'),
    path('simulate_demos', views.simulate_demos, name='simulate_demos'),
    path('normalize_scores', views.normalize_scores, name='normalize_scores')
]
