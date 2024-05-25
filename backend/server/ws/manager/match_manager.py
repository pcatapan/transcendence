from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
import logging

logger = logging.getLogger(__name__)


class MatchManager():
	list_of_players = {}

	def __init__(self):
		pass

	def inzialize_list_of_players(self, match_id, client_id, consumer):
		if not self.list_of_players.get(match_id):
			self.list_of_players[match_id] = {}
		self.list_of_players[match_id][client_id] = consumer

	def get_list_of_players_rtr(self, match_id):
		return list(self.list_of_players[match_id].keys()),

	def add_player(self, player):
		self.list_of_players[str(player.id)] = player

	def get_match_and_player(self, match_id):
		Match = import_string('api.tournament.models.match')
		match = Match.objects.select_related('player1', 'player2').get(id=match_id)

		if match:
			return match
		
		return None
	
	def get_defoult_keyboard(self, player_id):
		return {
			'up': f"up.{player_id}",
			'down': f"down.{player_id}",
			'left': False,
			'right': False,
			'space': False,
		}
	
	def player_in_list(self, player_id, match_id):
		return player_id in self.list_of_players[match_id]