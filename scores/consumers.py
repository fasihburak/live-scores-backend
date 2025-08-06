import json
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.decorators import user_passes_test

logger = logging.getLogger(__name__)


def admin_required(user):
    return user.is_staff  # or user.is_superuser


class EventConsumer(WebsocketConsumer):
    def connect(self):
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        # print('USER', self.scope['user'])
        # logger.info(f"Receiving message from user: {self.scope['user']}")
        self.match_group_name = f"chat_{self.match_id}"

        # Join match group
        async_to_sync(self.channel_layer.group_add)(
            self.match_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave match group
        async_to_sync(self.channel_layer.group_discard)(
            self.match_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        # Only allow admin users to send messages
        user = self.scope.get('user')
        if not user or not user.is_staff:
            self.send(text_data=json.dumps({"error": "Only admin users may send messages."}))
            return
        text_data_json = json.loads(text_data)
        print(type(text_data_json))
        print('text_data_json', text_data_json)
        message = text_data_json["message"]

        # Send message to match group
        async_to_sync(self.channel_layer.group_send)(
            self.match_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from match group
    def event_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))