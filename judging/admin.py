from django.contrib import admin
from .models import Organization, Team, Category, Demo

admin.site.register(Organization)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Demo)
