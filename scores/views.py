from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError, NotFound
from .models import Match, Team, Person, InMatchEvent, Competition
from .serializers import (
    GroupSerializer, UserSerializer, MatchSerializer, 
    TeamSummarySerializer, TeamSerializer, PersonSerializer,
    InMatchEventSerializer, CompetitionSerializer
    )
from .permissions import IsAdminOrReadOnly
from .filters import MatchFilter

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


class BaseAuthorizedViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrReadOnly]


class CompetitionViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows competitions to be viewed or edited.
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer


class MatchViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows matches to be viewed or edited.
    """
    queryset = Match.objects.all().order_by('match_date')
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MatchFilter
    

class TeamViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows teams to be viewed or edited.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PersonViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows persons to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class InMatchEventViewSet(BaseAuthorizedViewSet):
    """
    API endpoint that allows in-match events to be viewed or edited.
    """
    queryset = InMatchEvent.objects.all()
    serializer_class = InMatchEventSerializer

    def get_queryset(self):
        match_pk = self.kwargs.get('match_pk')
        if match_pk is None:
            raise ValidationError("match_pk cannot be null.")
        # Check if the match exists
        if not Match.objects.filter(pk=match_pk).exists():
            raise NotFound(f"Match with id '{match_pk}' not found.")
        return InMatchEvent.objects.filter(match_id=match_pk).order_by('-minute')
    