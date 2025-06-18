from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .models import Match, Team, Person, InMatchEvent
from .serializers import (
    GroupSerializer, UserSerializer, MatchSerializer, 
    TeamSummarySerializer, TeamSerializer, PersonSerializer,
    InMatchEventSerializer
    )
from .permissions import IsAdminOrReadOnly


def view_match(request, match_id):
    match = Match.objects.get(id=match_id)
    return render(request, "scores/match.html", {"match": match})

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class BaseAuthorizedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]


class MatchViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows matches to be viewed or edited.
    """
    queryset = Match.objects.all().order_by('match_date')
    serializer_class = MatchSerializer


class TeamViewSet(BaseAuthorizedViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PersonViewSet(BaseAuthorizedViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class InMatchEventViewSet(BaseAuthorizedViewSet):
    queryset = InMatchEvent.objects.all()
    serializer_class = InMatchEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        match_id = self.request.query_params.get('match')
        if match_id:
            queryset = queryset.filter(match_id=match_id)
            # If the match_id is given, order by minute.
            return queryset.order_by('minute')