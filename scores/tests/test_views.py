import uuid
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from scores.models import Match, InMatchEvent, Person

@pytest.mark.django_db
def test_inmatch_events_not_found_for_missing_match():
    match_pk = uuid.UUID(int=0)
    client = APIClient()
    # Use a match_pk that does not exist
    response = client.get(f'/api/matches/{match_pk}/in-match-events/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.data["detail"].lower()

@pytest.mark.django_db
def test_inmatch_events_list_for_existing_match():
    client = APIClient()
    # Create a person (player)
    person = Person.objects.create(given_name="Hagi")
    # Create a match
    match = Match.objects.create(pk=uuid.uuid4())
    # Create two events for this match
    event1 = InMatchEvent.objects.create(match=match, minute=10, 
                                         event_type="goal", person=person)
    event2 = InMatchEvent.objects.create(match=match, minute=20, 
                                         event_type="yellow_card", person=person)
    # Request events for the match
    response = client.get(f'/api/matches/{match.pk}/in-match-events/')
    assert response.status_code == status.HTTP_200_OK
    # Check that both events are returned
    returned_minutes = [e["minute"] for e in response.data['results']]
    assert set(returned_minutes) == {10, 20}
    # Optionally, check event types
    returned_types = [e["event_type"] for e in response.data['results']]
    assert set(returned_types) == {"goal", "yellow_card"}