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
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
import users
import applications
import administration
import mentors
import judging
from . import views 

urlpatterns = [
    path('administration/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^apps/', include('applications.urls')),
    url(r'^admin/', include('administration.urls')),
    url(r'^mentor/', include('mentors.urls')),
    url(r'^judging/', include('judging.urls')),
    path('', users.views.redirect_dashboard),
    path('emails/<str:email_uuid>', views.receive_email),
    path('reset/<str:email_uuid>', users.views.reset_password),
    path('logout', users.views.logout_view),
    path('dashboard', users.views.dashboard),
    path('application', applications.views.application),
    path('confirmation', applications.views.confirmation),
    path('tickets', mentors.views.tickets_main),
    path('tickets/create', mentors.views.create_ticket),
    path('tickets/delete', mentors.views.delete_ticket),
    path('make/mentor', mentors.views.make_mentor_manual),
    path('make/judge', judging.views.make_judge_manual),
    path('make/admin', administration.views.make_admin_manual),
    path('download/resumes/<str:gradYear>', mentors.views.download_resumes),
    path('download/resume/me/<str:uid>', mentors.views.get_resume_by_id),
    path('download/my/resume', mentors.views.get_my_resume),
    path('setup', users.views.setup, name='setup')
]
