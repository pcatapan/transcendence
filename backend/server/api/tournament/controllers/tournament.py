from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
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

@transaction.atomic
@require_GET
def createNextRound(tournament_id):
	tournament = Tournament.objects.get(id=tournament_id)

	current_round = tournament.round
	matches = LocalMatch.objects.filter(tournament=tournament, round=current_round, played=True)

	if not matches.exists():
		return JsonResponse({'message': 'All matches must be played before creating the next round'}, status=422)
	
	winners = []
	for match in matches:
		if match.winner:
			winners.append(match.winner)

	if len(winners) == 1:
		return JsonResponse({
			'message': 'The tournament has finished',
			'data': {
				'winner': winners[0].name
			}
		}, status=422)
	
	if len(winners) == 0:
		return JsonResponse({'message': 'No winners found'}, status=422)
	
	tournament.round += 1
	tournament.save()

	next_round = tournament.round
	next_round_matches = []
	for i in range(0, len(winners), 2):
		if i + 1 < len(winners):
			player1 = winners[i]
			player2 = winners[i + 1]
		else:
			player1 = winners[i]
			player2 = None

		match = LocalMatch.objects.create(
			player1=player1,
			player2=player2,
			tournament=tournament,
			round=next_round
		)
		next_round_matches.append(match)

	return JsonResponse({
		'data': {
			'round': next_round,
			'tournament': tournament.to_json(),
			'matches': [match.to_json() for match in next_round_matches]
		},
		'message': 'Next round created successfully'
	})
	