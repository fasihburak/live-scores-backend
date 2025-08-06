import json
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

@extend_schema_view(
    get=extend_schema(
        summary="WebSocket: Events in a match room",
        description=(
            "Connect to this WebSocket endpoint to receive in-match-events in real-time.\n\n"
            "**Endpoint:** `ws/matches/{match_id}/in-match-events/`\n\n"
            "**Protocols:** WebSocket\n\n"
            "**Example message:**\n"
            "```json\n"
            "{\n"
            "    \"id\": \"322e605d-1074-42f7-9a62-063c225f2961\",\n"
            "    \"event_type\": \"card\",\n"
            "    \"minute\": 4,\n"
            "    \"detail\": null,\n"
            "    \"color\": \"red\",\n"
            "    \"goal_type\": null,\n"
            "    \"person\": {\n"
            "        \"given_name\": \"Hagi\",\n"
            "        \"middle_name\": null,\n"
            "        \"family_name\": null\n"
            "    },\n"
            "    \"other_player\": null,\n"
            "    \"operation_type\": \"update\",\n"
            "    \"message_type\": \"in_match_event\"\n"
            "}\n"
            "```\n"
            "```"
        ),
        tags=["websockets"]
    )
)
class WebSocketDocumentationView(APIView):
    """
    This is a dummy view to document the WebSocket endpoint.
    """

    def get(self, request, *args, **kwargs):
        return Response({"detail": "This endpoint is for documentation only."})
