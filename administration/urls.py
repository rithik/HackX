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
   path('', views.admin_main),
   path('users', views.admin_users),
   path('qr', views.admin_qr),
   path('qr/settings', views.admin_qr_settings),
   path('nametags', views.admin_make_nametags),
   path('makeAdmin/<int:user_id>', views.make_admin),
   path('qr/update/<str:typ>/<str:num>/<str:tf>', views.qr_request),
   path('acceptUser/<int:user_id>', views.accept_user),
   path('waitlistUser/<int:user_id>', views.waitlist_user),
   path('rejectUser/<int:user_id>', views.reject_user),
   path('organizations', views.view_organizations),
   path('create_judges', views.create_judges),
   path('settings', views.admin_settings, name='admin_settings'),
   path('export_applications_csv', views.admin_export_csv, name='admin_export_csv'),
   path('verify_all_users', views.verify_all_users),
   path('remind_incomplete_users', views.remind_incomplete_applications),
   path('send_incomplete_email', views.send_incomplete_email)
]
