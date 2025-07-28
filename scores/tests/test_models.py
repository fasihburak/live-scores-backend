import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import patch
from ..models import Competition, Team, Match
from .. import signals

@pytest.mark.django_db(transaction=True)
def test_db_write_read():
    competition = Competition(name="Test Competition")
    competition.save()
    assert competition.id is not None
    retrieved_competition = Competition.objects.get(id=competition.id)
    assert retrieved_competition.name == "Test Competition"


@pytest.mark.django_db
def test_get_competitions_endpoint():
    client = APIClient()
    # Create a competition in the database
    competition = Competition.objects.create(name="Test Competition")
    # Make a GET request to the competitions endpoint
    response = client.get(f'/api/competitions/{competition.id}/')
    # Assert the response status code
    assert response.status_code == 200
    # Assert the response contains the created competition
    print(response.json())
    assert response.json()['name'] == "Test Competition"


@pytest.mark.django_db
def test_get_match():
    client = APIClient()
    # Create a competition in the database
    competition = Competition.objects.create(name="Test Competition")
    # Create a team associated with the competition
    team_1 = Team.objects.create(name="Team 1")
    team_2 = Team.objects.create(name="Team 2")
    match = Match.objects.create(
        first_team=team_1, second_team=team_2, competition=competition,
        match_date=timezone.now(), status='some-status'
        )
    response = client.get(f'/api/matches/{match.id}/')
    assert response.status_code == 200
    assert response.json()['id'] == str(match.id)


@pytest.mark.django_db
def test_message_sent_on_match_update():
    client = APIClient()
    # Create a competition in the database
    competition = Competition.objects.create(name="Test Competition")
    # Create a team associated with the competition
    team_1 = Team.objects.create(name="Team 1")
    team_2 = Team.objects.create(name="Team 2")
    match = Match.objects.create(
        first_team=team_1, second_team=team_2, competition=competition,
        match_date=timezone.now(), status='some-status'
        )
    # Mock the send_message_to_group function
    with patch.object(signals, 'send_message_to_group') as mock_send_message:
    # with patch('scores.signals.send_message_to_group') as mock_send_message: # This one is also correct
        match.status = 'updated-status'
        match.save()
        print('mock_send_message:', mock_send_message)
        args = (
            'chat_' + str(match.id), 
            {
                'message_type': 'match', 'operation_type': 'update', 'status': 'updated-status', 
                'first_team_goals_scored': None, 'second_team_goals_scored': None
            }
        )
        mock_send_message.assert_called_once_with(*args)

def test_fail():
    assert 1 == 0
