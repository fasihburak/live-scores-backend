from django.contrib import admin
from .models import (
    Person, Role, InMatchEvent, Team, Match, Competition
)


class InMatchEventInline(admin.TabularInline):
    model = InMatchEvent
    extra = 0
    ordering = ['minute']  # order events by minute

class MatchAdmin(admin.ModelAdmin):
    inlines = [InMatchEventInline]
    list_display = ['__str__']


admin.site.register(Person)
admin.site.register(Role)
admin.site.register(InMatchEvent)
admin.site.register(Team)
admin.site.register(Match, MatchAdmin)
admin.site.register(Competition)
