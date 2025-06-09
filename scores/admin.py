import logging
import requests
from django.contrib import admin
from .models import (
    Person, Role, InMatchEvent, Team, Match, Competition
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def send_message_to_group(group_name, message):
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message",  # This should match your consumer's method
                "message": message,
            }
        )
        logger.info(f"Message sent to group {group_name}: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to group {group_name}: {e}")


# def send_chat_message(message):
#     # Replace 'https://your-chat-webhook-url' with your actual chat webhook URL
#     webhook_url = 'http://localhost/ws/chat/abcroom/'
#     payload = {"text": message}
#     requests.post(webhook_url, json=payload)


class InMatchEventInline(admin.TabularInline):
    model = InMatchEvent
    extra = 0
    ordering = ['minute']  # order events by minute


class MatchAdmin(admin.ModelAdmin):
    inlines = [InMatchEventInline]
    list_display = ['__str__']

    def save_model(self, request, obj, form, change):
        if change:
            old_match_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = {}
            for field in obj._meta.fields:
                field_name = field.name
                old_value = getattr(old_match_obj, field_name)
                new_value = getattr(obj, field_name)
                if old_value != new_value:
                    print('FIELD', field)
                    if field == type(obj)._meta.get_field('first_team_goals_scored'):
                        print('Caught it!')
                        send_message_to_group(group_name='chat_abcroom', message='qwert')
                        # send_chat_message(message='ABBB')
                    changed_fields[field_name] = (old_value, new_value)

            if changed_fields:
                logger.info(f"Change captured in {obj}:")
                for field, (old, new) in changed_fields.items():
                    logger.info(f"  {field}: {old} -> {new}")
                    print('fieldtype', type('field'))

        super().save_model(request, obj, form, change)


admin.site.register(Person)
admin.site.register(Role)
admin.site.register(InMatchEvent)
admin.site.register(Team)
admin.site.register(Match, MatchAdmin)
admin.site.register(Competition)
