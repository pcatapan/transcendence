import os
import django
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string

from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)


class MatchManager():
	list_of_players = {}

	def __init__(self):
		pass

	def inzialize_list_of_players(self, match_id, client_id, consumer):
		try :
			if not self.list_of_players.get(match_id):
				self.list_of_players[match_id] = {}
			self.list_of_players[match_id][client_id] = consumer
		except Exception as e:
			logger.error(f"Error in inzialize_list_of_players: {e}")

	def get_list_of_players_rtr(self, match_id):
		try :
			return list(self.list_of_players[match_id].keys()),
		except Exception as e:
			logger.error(f"Error in get_list_of_players_rtr: {e}")
			return []

	def add_player(self, player):
		try :
			self.list_of_players[str(player.id)] = player
		except Exception as e:
			logger.error(f"Error in add_player: {e}")

	@database_sync_to_async
	def get_match_and_player(self, match_id):
		from api.tournament.models import Match

		try:	
			match = Match.objects.select_related('player1', 'player2').get(id=match_id)
		except Exception as e:
			logger.error(f"Error in get_match_and_player: {e}")

		if match:
			return match
		
		logger.error(f"Match not found")
		return None

	def get_match_atomic(self, match_id):
		try :
			from api.tournament.models import Match

			match = Match.objects.select_for_update().get(id=match_id)

			if match:
				return match

			return None
		except Exception as e:
			logger.error(f"Error in get_match_atomic: {e}")
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
		try :
			if len(self.list_of_players) == 0:
				return False

			return player_id in self.list_of_players[match_id]
		except Exception as e:
			logger.error(f"Error in player_in_list: {e}")
			return False
	
	def remove_player(self, match_id, player_id):
		try :
			del self.list_of_players[match_id][player_id]
		except Exception as e:
			logger.error(f"Error in remove_player: {e}")