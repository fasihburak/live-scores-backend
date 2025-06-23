import logging
from enum import Enum
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from django.contrib.auth.models import Group, User
from .models import Match, InMatchEvent, Team, Person

logger = logging.getLogger(__name__)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class PersonSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ['given_name', 'middle_name', 'family_name']   


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ['given_name', 'middle_name', 'family_name', 'birth_date']   


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    people = PersonSummarySerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'logo', 'name', 'people']


class TeamSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'logo', 'name']       


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    first_team = TeamSummarySerializer(read_only=True)
    second_team = TeamSummarySerializer(read_only=True)
    class Meta:
        model = Match
        fields = ['id', 'match_date', 'first_team', 'second_team', 'status',
                  'first_team_goals_scored', 'second_team_goals_scored']


class InMatchEventSerializer(serializers.ModelSerializer):
    person = PersonSummarySerializer(read_only=True)
    other_player = PersonSummarySerializer(read_only=True)

    class Meta:
        model = InMatchEvent
        fields = '__all__'

class MessageType(Enum):
    MATCH = "match"
    IN_MATCH_EVENT = "in_match_event"


MESSAGE_TYPE_CHOICES = [(tag.value, tag.value) for tag in MessageType]


class OperationType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


OPERATION_TYPE_CHOICES = [(tag.value, tag.value) for tag in OperationType]


class MessageSerializerMatch(serializers.HyperlinkedModelSerializer):
    # Define a constant custom_field; read_only and a default value ensure it's constant.
    message_type = serializers.ChoiceField(choices=MESSAGE_TYPE_CHOICES, 
                                           read_only=True, 
                                           default=MessageType.MATCH.value)
    operation_type = serializers.ChoiceField(choices=OPERATION_TYPE_CHOICES,
                                             default=OperationType.CREATE.value,
                                             read_only=True)
    
    class Meta:
        model = Match
        fields = ['message_type', 'operation_type', 'status', 'first_team_goals_scored', 
                  'second_team_goals_scored']

    def validate(self, data):
        if not any(data.get(field) is not None for field in self.Meta.fields):
            raise serializers.ValidationError(
                "At least one of the fields 'status', 'first_team_goals_scored', or " \
                "'second_team_goals_scored' must be provided."
            )
        return data
    

class MessageSerializerInMatchEvent(serializers.HyperlinkedModelSerializer):
    # Define a constant custom_field; read_only and a default value ensure it's constant.
    message_type = serializers.ChoiceField(choices=MESSAGE_TYPE_CHOICES, 
                                           default=MessageType.IN_MATCH_EVENT.value,
                                           read_only=True) 
    operation_type = serializers.ChoiceField(choices=OPERATION_TYPE_CHOICES,
                                             default=OperationType.CREATE.value,
                                             read_only=True)
    
    class Meta:
        model = InMatchEvent

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Merge in operation_type from initial_data if provided
        if hasattr(self, 'initial_data'):
            rep['operation_type'] = self.initial_data.get('operation_type')
            rep['message_type'] = self.initial_data.get('message_type')
        return rep


class MessageSerializerCreateUpdateInMatchEvent(MessageSerializerInMatchEvent):
    '''
    Serializer to use when a new InMatchEvent object is created or an already 
    existing object is updated.
    '''

    person = PersonSummarySerializer(read_only=True)
    other_player = PersonSummarySerializer(read_only=True)

    class Meta(MessageSerializerInMatchEvent.Meta):
        fields = ["id", "message_type", "operation_type", "event_type", "minute",
                  "detail", "color", "goal_type", "person", "other_player"]
    

class MessageSerializerDeleteInMatchEvent(MessageSerializerInMatchEvent):
    '''
    Serializer to use when an InMatchEvent object is deleted.
    '''

    class Meta(MessageSerializerInMatchEvent.Meta):
        fields = ["id", "message_type", "operation_type"]


def send_message_to_group(group_name, message):
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "event_message",  # This should match your consumer's method
                "message": message,
            }
        )
        logger.info(f"Message sent to group {group_name}: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to group {group_name}: {e}")