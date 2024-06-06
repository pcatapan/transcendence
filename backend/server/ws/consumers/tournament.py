import json
import time
import logging
import asyncio
from typing import Dict, Optional, Any

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.module_loading import import_string
from django.utils import timezone
from django.db import transaction

from ..pong_object.game import Game
from ..pong_object.player import Player

from ..manager.tournament_manager import TournamentManager
from ..manager.match_manager import MatchManager
from ..utils.message import Message
from ..utils.game_base import GameBase
from .. import constants

logger = logging.getLogger(__name__)

class Tournament(AsyncWebsocketConsumer, Message, GameBase):
	tournament_manager = TournamentManager()
	match_manager = MatchManager()

	shared_game_keyboard = {}
	shared_game_task = {}
	shared_game = {}
	run_game = {}
	finished = {}
	scorelimit = constants.SCORE_LIMIT

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.client_object = None
		self.keyboard = {}
		self.left_player = None
		self.right_player = None
		self.player_1_id = None
		self.player_2_id = None
		self.player_1_score = 0
		self.player_2_score = 0
		self.match_object = None
		self.match_id = None
		self.tournament_id = None
		self.isLocal = False
		self.client_id = None

	async def connect(self):
		try:
			user = self.scope['user']
			if user.is_authenticated:
				self.player_object = user
			else:
				logger.error("User is not authenticated")
				await self.close(code=4001)
				return

			self.client_id = str(user.id)
			self.match_id = self.scope['url_route']['kwargs']['match_id']
			self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']

			# Controllo che il torneo esiste
			tournament = await self.tournament_manager.get_tournament(self.tournament_id)
			if not tournament:
				await self.close()
				return
			
			self.match_object = await self.tournament_manager.get_match_and_player(self.match_id)
			if not self.match_object:
				await self.close()
				return
			logger.info(f"Match obj : {self.match_object}")
			
			self.isLocal = True
			await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
			await self.load_models()

			await self.accept()

			await self.broadcast_layer(
				content="Game Ready",
				command=constants.START_BALL,
				channel=f"{self.match_id}"
			)
			
		except Exception as e:
			await self.close()
			logger.error(f"Error during connect: {e}")

	async def disconnect(self, code=1000):
		logger.info(f"Client {self.client_id} disconnected with code {code}")
		if code == 4001 or self.match_id is None:
			return

		Tournament.run_game[self.match_id] = False

		if not Tournament.finished[self.match_id]:
			await self.check_reconnect(1)

			try:
				res = await self.save_models(disconnect=True)
				if res:
					await self.broadcast_layer(
						command=constants.FINISH_MATCH,
						content="Opponent disconnected",
						channel=f"{self.match_id}"
					)
			except Exception as e:
				logger.error(f"Error during disconnect: {e}")

		await self.discard_channels()

	async def receive(self, text_data):
		logger.info(f"Receive: {text_data}")
		try:
			data = json.loads(text_data)
			command = data.get('command')

			handlers = {
				constants.KEYBOARD: self.handle_keyboard_input,
				constants.START_BALL: self.handle_start_game,
			}

			handler = handlers.get(command, self.handle_unknown_command)
			await handler(data)

		except json.JSONDecodeError as e:
			logger.error(f"JSON decode error: {e}")
		except Exception as e:
			logger.error(f"Error in receive method: {e}")

# -------------------------------------------------------------------------------------




# -------------------------------------- Handle ----------------------------------------
	async def handle_unknown_command(self, data):
		await self.send_json({'error': 'Unknown command'})

	async def handle_keyboard_input(self, data):
		if not Tournament.run_game[self.match_id]:
			logger.error(f"Game not started")
			await self.send_json({'error': 'Game not started'})
			return

		try:
			key_status = data.get('key_status')
			key = data.get('key')
			formatted_key = f'{key}.{self.player_1_id}'

			if self.isLocal:
				if key in ['w', 's']:
					formatted_key = f'{key}.{self.player_2_id}'

			key_status_map = {
				'on_press': True,
				'on_release': False,
			}

			await asyncio.sleep(0.01)
			if key_status in key_status_map:
				Tournament.shared_game_keyboard[self.match_id][formatted_key] = key_status_map[key_status]
			else:
				logger.error(f'Unknown key status: {key_status}, {formatted_key}')
				await self.send_json({'error': f'Unknown key status: {key_status}'})
					
		except KeyError:
			logger.error(f"Invalid key: {formatted_key}")
			await self.send_json({'error': 'Invalid key'})
		except Exception as e:
			logger.error(f"Error during keyboard_input: {e}")
			await self.close()

	async def handle_start_game(self, data):
		Tournament.run_game[self.match_id] = True
		Tournament.finished[self.match_id] = False
		
		Tournament.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(data))
# -------------------------------------------------------------------------------------




# -------------------------------------- Methods ----------------------------------------
	async def load_models(self):
		try:

			self.player_1_id = self.match_object.player1.id
			self.player_2_id = self.match_object.player2.id

			self.match_manager.inzialize_list_of_players(self.match_id, self.client_id, self)

			self.keyboard = {
				self.player_1_id: self.match_manager.get_defoult_keyboard(self.player_1_id),
				self.player_2_id: self.match_manager.get_defoult_keyboard(self.player_2_id, True)
			}

			self.left_player = Player(
				name=self.player_1_id,
				binds=self.keyboard[self.player_1_id]
			)

			self.right_player = Player(
				name=self.player_2_id,
				binds=self.keyboard[self.player_2_id]
			)

			keyboard = {
				f'up.{self.player_1_id}': False,
				f'down.{self.player_1_id}': False,

				f"w.{self.player_2_id}": False,
				f"s.{self.player_2_id}": False,
			}

			Tournament.shared_game_keyboard[self.match_id] = keyboard
			Tournament.run_game[self.match_id] = False

			Tournament.shared_game[self.match_id] = Game(
				dictKeyboard=Tournament.shared_game_keyboard[self.match_id],
				leftPlayer=self.left_player,
				rightPlayer=self.right_player,
				scoreLimit=self.scorelimit,
			)

		except Exception as e:
			logger.error(f"Error loading models: {e}")
			await self.close()

	@database_sync_to_async
	@transaction.atomic
	def save_models(self, disconnect: bool = False, close_code: int = 1000) -> Optional[Dict[str, Any]]:
		Player = import_string('api.tournament.models.Player')

		if Tournament.finished.get(self.match_id):
			return

		match_object = self.tournament_manager.get_match_atomic(self.match_id)
		game = Tournament.shared_game[self.match_id]
		player1_name = self.player_1_id
		player2_name = self.player_2_id

		match_object.player1_score = game._leftPlayer.score
		match_object.player2_score = game._rightPlayer.score

		if match_object.player1_score == match_object.player2_score:
			winner_name = None
		else:
			winner_name = player1_name if match_object.player1_score > match_object.player2_score else player2_name

		match_object.winner = Player.objects.get(id=winner_name) if winner_name else None
		match_object.date_played = timezone.now()
		match_object.active = False
		match_object.save()

		Tournament.finished[self.match_id] = True

		if match_object.winner:

			return {
				"winner_username": match_object.winner.name if match_object.winner else None,
				"loser_id": player1_name if winner_name == player2_name else player2_name,
				"player1_username": match_object.player1.name,
				"player1_score": match_object.player1_score,
				"player2_username": match_object.player2.name,
				"player2_score": match_object.player2_score,
			}
		else:
			logger.info(f"Match {self.match_id} ended in a tie.")
