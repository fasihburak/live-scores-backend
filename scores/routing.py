from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/in-game-events/(?P<match_id>[\w-]+)/$", consumers.EventConsumer.as_asgi()),
]