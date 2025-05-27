from django.shortcuts import render
from .models import Match

def view_match(request, match_id):
    match = Match.objects.get(id=match_id)
    return render(request, "scores/match.html", {"match": match})