import logging
import json
from typing_extensions import Self
from uuid import UUID
from enum import Enum
from django.contrib import admin
from rest_framework import serializers
from pydantic import BaseModel, model_validator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import (
    Person, Role, InMatchEvent, Team, Match, Competition
)

logger = logging.getLogger(__name__)


# class InMatchEventAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         # Determine the operation type based on whether the object is new or changed.
#         operation = 'update' if change else 'create'

#         # Serialize the InMatchEvent instance.
#         serializer = InMatchEventMessageSerializer(obj, context={'request': request})
#         message_data = serializer.data

#         # Override or set the operation_type field in the serialized data.
#         message_data['operation_type'] = operation

#         # Send the serialized message to the appropriate chat group by match_id.
#         send_message_to_group(
#             group_name='chat_' + str(obj.match_id),
#             message=json.dumps(message_data, default=str)
#         )

#         return super().save_model(request, obj, form, change)


class PersonTeamInline(admin.TabularInline):
    model = Team.people.through
    extra = 1
    fk_name = "person"


class PersonAdmin(admin.ModelAdmin):
    # Reverse side must be edited via the through-model inline:
    inlines = [PersonTeamInline]


class TeamCompetitionInline(admin.TabularInline):
    model = Competition.teams.through
    extra = 1
    fk_name = "team"


class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ("people",)
    inlines = [TeamCompetitionInline]


class InMatchEventInline(admin.TabularInline):
    model = InMatchEvent
    extra = 0
    ordering = ['minute']  # order events by minute

class CompetitionAdmin(admin.ModelAdmin):
    filter_horizontal = ("teams",)

class MatchAdmin(admin.ModelAdmin):
    inlines = [InMatchEventInline]
    list_display = ['__str__']

    # def save_model(self, request, obj, form, change):
    #     if change:
    #         print('CHANGED STH!')
    #         old_match_obj = self.model.objects.get(pk=obj.pk)
    #         changed_fields = {}
    #         # The fields of the model that trigger a message to be sent
    #         message_fields = [type(obj)._meta.get_field('status'),
    #                           type(obj)._meta.get_field('first_team_goals_scored'),
    #                           type(obj)._meta.get_field('second_team_goals_scored')]
    #         for field in obj._meta.fields:
    #             field_name = field.name
    #             old_value = getattr(old_match_obj, field_name)
    #             new_value = getattr(obj, field_name)
    #             if old_value != new_value:
    #                 print('FIELD', field)
    #                 if field in message_fields:
    #                     send_message_to_group(group_name='chat_' + str(obj.pk), 
    #                                           message=json.dumps({
    #                                               'operation':'update',
    #                                               field_name:new_value
    #                                               }
    #                                             )
    #                                         )
    #                 changed_fields[field_name] = (old_value, new_value)

    #         if changed_fields:
    #             logger.info(f"Change captured in {obj}:")
    #             for field, (old, new) in changed_fields.items():
    #                 logger.info(f"  {field}: {old} -> {new}")
    #                 print('fieldtype', type('field'))

    #     super().save_model(request, obj, form, change)

admin.site.register(Person, PersonAdmin)
admin.site.register(Role)
admin.site.register(Team, TeamAdmin)
# admin.site.register(InMatchEvent, InMatchEventAdmin)
admin.site.register(InMatchEvent)
admin.site.register(Match, MatchAdmin)
admin.site.register(Competition, CompetitionAdmin)
