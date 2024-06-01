import os
import django
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string

from .. import constants

from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)


class MatchManager():
	list_of_players = {}
	winner = None
	loser = None

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
	
	def update_elo(self, match_obj, player1_id):
		try :
			from api.authuser.models import CustomUser

			winner_id = match_obj.winner.id
			loser_id = match_obj.loser().id

			self.winner = CustomUser.objects.get(winner_id)
			self.loser = CustomUser.objects.get(loser_id)

			winner_score = match_obj.player1_score if winner_id == player1_id else match_obj.player2_score
			loser_score = match_obj.player2_score if winner_id == player1_id else match_obj.player1_score
			score_margin = (winner_score - loser_score) * constants.ELO_MOLTIPLIER

			elo_change = constants.ELO_BASE + score_margin

			self.winner.ELO = max(0, self.winner.ELO + elo_change)
			self.loser.ELO = max(0, self.loser.ELO - elo_change)

			self.winner.save()
			self.loser.save()
		except Exception as e:
			logger.error(f"Error in update_elo: {e}")