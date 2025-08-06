from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r"api/ws/matches/<uuid:match_id>/in-match-events/", consumers.EventConsumer.as_asgi()),
]
# /matches/{match_pk}/in-match-events/
# path("matches/<uuid:match_id>/", view_match),