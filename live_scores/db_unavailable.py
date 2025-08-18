import os
from datetime import datetime, timezone
from django.http import HttpResponse

class UnavailableMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not int(os.environ['DEBUG']):
            now = datetime.now(timezone.utc)
            if now.weekday() > 4 or (now.hour > 17 or now.hour < 13):
                return HttpResponse(
                    "Service is only available on weekdays between 13:00 and 17:00 UTC.",
                    status=503
                )
        return self.get_response(request)