from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from api.authuser.models.custom_user import CustomUser
from api.tournament.models.match import Match
from api.tournament.models.tournament import Tournament

@require_GET
def get_kpi(request):
	user = get_object_or_404(CustomUser, pk=user_id)

	matches = Match.objects.filter(Q(player1=user) | Q(player2=user))
	#matches = [x for x in matches if x.winner]#

	wins = [x for x in matches if x.winner == user]
	winrate = round(len(wins) / len(matches), 2) if len(matches) != 0 else 0
	tournament_wins = Tournament.objects.filter(winner=user)

	return JsonResponse({
		"games_played": len(matches),
		"wins": len(wins),
		"winrate": winrate * 100,
		"tournaments_won": len(tournament_wins),
	}, status=200)