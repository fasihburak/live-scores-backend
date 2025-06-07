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

    def save_model(self, request, obj, form, change):
        if change:
            old_match = self.model.objects.get(pk=obj.pk)
            changed_fields = {}
            for field in obj._meta.fields:
                field_name = field.name
                old_value = getattr(old_match, field_name)
                new_value = getattr(obj, field_name)
                if old_value != new_value:
                    changed_fields[field_name] = (old_value, new_value)

            if changed_fields:
                print(f"Changed fields for {obj}:")
                for field, (old, new) in changed_fields.items():
                    print(f"  {field}: {old} -> {new}")

        super().save_model(request, obj, form, change)


admin.site.register(Person)
admin.site.register(Role)
admin.site.register(InMatchEvent)
admin.site.register(Team)
admin.site.register(Match, MatchAdmin)
admin.site.register(Competition)
