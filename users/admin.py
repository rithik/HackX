from django.contrib import admin
from .models import User, EmailView, Ticket, PuzzleTeam

class EmailViewAdmin(admin.ModelAdmin):
    readonly_fields = ('sent', 'viewed')

admin.site.register(User)
admin.site.register(EmailView, EmailViewAdmin)
admin.site.register(Ticket)
admin.site.register(PuzzleTeam)
