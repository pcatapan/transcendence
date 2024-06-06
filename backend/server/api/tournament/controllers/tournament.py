from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views import View
import math
import json
import random
from ..models import Tournament, Player, LocalMatch

@require_POST
def post(request):
	if not request.body:
		return JsonResponse({'message': 'Empty payload'}, status=400)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)

	name = data.get('name')
	if not name:
		return JsonResponse({'message': "The 'name' field is required"}, status=422)

	type = data.get('type', '1v1')
	player_names = data.get('player_names', [])

	if not player_names:
		return JsonResponse({'message': "At least one player name is required"}, status=422)
	
	player_names.append(request.user.username)
	
	# controllo che i valori di player_names siano univoci
	if len(player_names) != len(set(player_names)):
		return JsonResponse({'message': "Player names must be unique"}, status=422)

	tournament = Tournament(
		name=name,
		type=type,
		tournament_admin=request.user
	)

	try:
		tournament.save()

		# Create players
		players = [Player.objects.create(name=player_name, tournament=tournament) for player_name in player_names]

		# Create rounds and matches
		matches = create_matches_round_1(tournament, players)
	except Exception as e:
		tournament.delete()
		return JsonResponse({'message': str(e)}, status=400)

	response = JsonResponse({
		'data': {
			'tournament': tournament.to_json(),
			'players': [player.name for player in players],
			'matches': [match.to_json() for match in matches]
		},
		'message': 'Tournament created successfully'
	})

	return response

def create_matches_round_1(tournament, players):
	random.shuffle(players)

	# Creazione dei match del primo round
	round_number = 1
	matches = []
	for i in range(0, len(players), 2):
		if i + 1 < len(players):
			player1 = players[i]
			player2 = players[i + 1]
		else:
			player1 = players[i]
			player2 = None

		match = LocalMatch.objects.create(
			player1=player1,
			player2=player2,
			tournament=tournament,
			round=round_number
		)
		matches.append(match)
	
	return matches

	