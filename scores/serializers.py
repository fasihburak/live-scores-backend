from django.contrib.auth.models import Group, User
from .models import Match, Team, Person
from rest_framework import serializers


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

 
