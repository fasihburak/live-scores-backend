import json
import logging
from django.db.models.signals import post_save, post_delete
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


@receiver(post_delete, sender=InMatchEvent)
def in_match_event_post_delete(sender, instance, **kwargs):
    # Serialize the deleted instance. Although it's been removed from the DB,
    # the instance data is still available in memory for serialization.
    serializer = MessageSerializerDeleteInMatchEvent(instance, context={'request': None})
    message_data = serializer.data
    message_data['operation_type'] = OperationType.DELETE.value
    group_name = 'chat_' + str(instance.match_id)
    message = json.dumps(message_data, default=str)
    send_message_to_group(group_name, message)
    logger.info(f"Sent in-match event deletion message for {instance.pk}")


@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    # Send the message only if a Match object is updated.
    if not created:
        serializer = MessageSerializerMatch(instance, context={'request': None})
        message_data = serializer.data
        message_data['operation_type'] = OperationType.CREATE.value
        group_name = 'chat_' + str(instance.id)
        message = json.dumps(message_data, default=str)
        send_message_to_group(group_name, message)
        logger.info(f"Sent match update message for {instance.pk}")

