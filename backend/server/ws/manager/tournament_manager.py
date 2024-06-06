import random
from django.utils import timezone
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async

import logging

logger = logging.getLogger(__name__)

class TournamentManager:
	@database_sync_to_async
	def get_match_and_player(self, match_id):
		from api.tournament.models import LocalMatch

		try:	
			match = LocalMatch.objects.select_related('player1', 'player2').get(id=match_id)
		except Exception as e:
			logger.error(f"Error in get_match_and_player: {e}")

		if match:
			return match
		
		logger.error(f"Match not found")
		return None
	
	@database_sync_to_async
	def get_tournament(self, tournament_id):
		from api.tournament.models import Tournament

		try:
			tournament = Tournament.objects.get(id=tournament_id)
		except Exception as e:
			logger.error(f"Error in get_tournament: {e}")

		if tournament:
			return tournament
		
		logger.error(f"Tournament not found")
		return None