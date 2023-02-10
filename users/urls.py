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
from django.conf.urls import include
from django.urls import path
from . import views 

urlpatterns = [
   path(r'login/', views.login_page, name='login_page'),
   path(r'forgot/', views.forgot_password, name='forgot_password'),
   path(r'register/', views.register_page, name='register_page'),
   path(r'resend/', views.resend_verification, name='resend_verification')
]
