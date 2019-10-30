from django.contrib import admin
from .models import User, EmailView, Ticket

admin.site.register(User)
admin.site.register(EmailView)
admin.site.register(Ticket)
