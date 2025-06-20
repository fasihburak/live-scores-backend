import json
import logging
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import InMatchEvent, Match
from .serializers import (
    MessageSerializerMatch,
    MessageSerializerCreateUpdateInMatchEvent, 
    MessageSerializerDeleteInMatchEvent,
    MessageType,
    OperationType,
    send_message_to_group
) 

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InMatchEvent)
def in_match_event_post_save(sender, instance, created, **kwargs):
    '''Do not use pre_save for this receiver because checking if instance.pk
    exists will always return true because instance.pk is pre-populated by the ORM.'''

    operation = OperationType.CREATE.value if created else OperationType.UPDATE.value
    data = {}
    data['operation_type'] = operation
    data['message_type'] = MessageType.IN_MATCH_EVENT.value
    serializer = MessageSerializerCreateUpdateInMatchEvent(instance, 
                                               data=data,
                                               context={'request': None},
                                               partial=True)
    serializer.is_valid(raise_exception=True)
    message_data = serializer.data
    print('message_data', message_data)
    group_name = 'chat_' + str(instance.match_id)
    message = json.dumps(message_data, default=str)
    send_message_to_group(group_name, message)
    logger.info(f"Sent in-match event {operation} message for {instance.pk}")


@receiver(pre_delete, sender=InMatchEvent)
def in_match_event_pre_delete(sender, instance, **kwargs):
    logger.info(f"In-match event {instance.pk} is about to be deleted.")
    serializer = MessageSerializerDeleteInMatchEvent(instance, context={'request': None})
    message_data = serializer.data
    message_data['operation_type'] = OperationType.DELETE.value
    group_name = 'chat_' + str(instance.match_id)
    message = json.dumps(message_data, default=str)
    send_message_to_group(group_name, message)
    logger.info(f"Sent in-match event deletion message for {instance.pk}")


@receiver(pre_save, sender=Match)
def match_pre_save(sender, instance, **kwargs):
    '''Do not use post_save for this receiver because "created" argument 
    will return True even if there is a change in a related field. So, it makes sense
    to use pre_save and compare the fields on the old object and the new one.'''
    if instance.pk: 
        old_instance = sender.objects.get(pk=instance.pk) 

        # Compare specific fields – here you can add more comparisons as needed.
        if old_instance.status != instance.status or \
        old_instance.first_team_goals_scored != instance.first_team_goals_scored or \
        old_instance.second_team_goals_scored != instance.second_team_goals_scored:
            logger.info(f"Changes detected in Match {instance.pk}")
            
            # Now you can create your message with the new state
            serializer = MessageSerializerMatch(instance, context={'request': None})
            message_data = serializer.data
            message_data['operation_type'] = OperationType.UPDATE.value

            group_name = 'chat_' + str(instance.id)
            message = json.dumps(message_data, default=str)
            send_message_to_group(group_name, message)
            logger.info(f"Sent match update message for {instance.pk}")
