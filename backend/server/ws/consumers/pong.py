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
from ..manager.match_manager import MatchManager
from ..utils.message import Message
from ..utils.game_base import GameBase
from .. import constants

logger = logging.getLogger(__name__)

class Pong(AsyncWebsocketConsumer, Message, GameBase):
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
		self.isAi = False
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
			# se il march_id contiene la stringa '_vs_ia_' allora si tratta di una partita contro l'IA
			if constants.AI_PREFIX_MATCH in self.match_id:
				self.isAi = True
				logger.info(f"Match ID: {self.match_id}")
				await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
				await self.load_models()
				
				await self.accept()

				await self.broadcast_layer(
					content="Game Ready",
					command=constants.START_BALL,
					channel=f"{self.match_id}"
				)
				return
			
			if constants.LOCAL_PREFIX_MATCH in self.match_id:
				self.isLocal = True
				logger.info(f"Match ID: {self.match_id}")
				await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
				await self.load_models()
				
				await self.accept()

				await self.broadcast_layer(
					content="Game Ready",
					command=constants.START_BALL,
					channel=f"{self.match_id}"
				)
				return
			#self.room_group_name = f'match_{self.match_id}'

			self.match_object = await self.match_manager.get_match_and_player(self.match_id)
			if not self.match_object:
				await self.close()
				return
			logger.info(f"Match obj : {self.match_object}")
			
			if user.id not in {self.match_object.player1.id, self.match_object.player2.id}:
				logger.info(f"User {self.client_id} is in the match {self.match_id}")
				await self.close()
				return

			if self.match_object.active:
				logger.error(f"Match {self.match_id} is active")
				await self.close(code=4001)
				return

			if self.match_object.winner_id:
				logger.error(f"Match {self.match_id} has already a winner")
				await self.close(code=4001)
				return

			await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
			# da valutare se serve
			await self.channel_layer.group_add(f"{self.match_id}.player.{self.client_id}", self.channel_name)

			await self.load_models()

			await self.accept()

			Pong.finished[self.match_id] = False

			await self.broadcast_layer(
				content={
					"message": "User Connected",
					"command":constants.CONNECTED_USERS,
					"connected_users": self.match_manager.get_list_of_players_rtr(self.match_id)
				},
				channel=f"{self.match_id}"
			)
			
			if self.match_manager.player_in_list(self.player_1_id, self.match_id) and \
			self.match_manager.player_in_list(self.player_2_id, self.match_id):
				await self.broadcast_layer(
					content="Game Ready",
					command=constants.START_BALL,
					channel=f"{self.match_id}"
				)
			else:
				await self.broadcast_layer(
					content="Waiting for opponent, please wait",
					command=constants.WAITING_FOR_OPPONENT,
					channel=f"{self.match_id}"
				)
				  
		except Exception as e:
			await self.close()
			logger.error(f"Error during connect: {e}")

	async def disconnect(self, code=1000):

		logger.info(f"Client {self.client_id} disconnected with code {code}")
		if (code == 4001 or self.match_id is None or self.isAi):
			return

		if self.match_manager.player_in_list(self.client_id, self.match_id):
			self.match_manager.remove_player(self.match_id, self.client_id)

		Pong.run_game[self.match_id] = False

		if not Pong.finished[self.match_id]:
			await self.check_reconnect()

			try:
				res = await self.save_models(disconnect=True)
				if res:
					await self.broadcast_layer(
						command=constants.FINISH_MATCH,
						content=res,
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
				constants.KEYBOARD: self.handle_keyboard_input, # Fatto
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
		
		if not Pong.run_game[self.match_id]:
			logger.error(f"Game not started")
			await self.send_json({'error': 'Game not started'})
			return

		try:
			key_status = data.get('key_status')
			key = data.get('key')
			formatted_key = f'{key}.{self.client_id}'

			if self.isLocal:
				if key in ['w', 's']:
					formatted_key = f'{key}.Guest'

			key_status_map = {
				'on_press': True,
				'on_release': False,
			}

			await asyncio.sleep(0.01)
			if key_status in key_status_map:
				Pong.shared_game_keyboard[self.match_id][formatted_key] = key_status_map[key_status]
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
		Pong.run_game[self.match_id] = True
		Pong.finished[self.match_id] = False

		Pong.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(data))

# -------------------------------------------------------------------------------------




# -------------------------------------- Methods ----------------------------------------
	async def load_models(self):
		try:
			self.player_1_id = self.client_id
			if self.isAi :
				self.player_2_id = 'AI'
			elif self.isLocal :
				self.player_2_id = 'Guest'
			else :
				self.player_1_id = self.match_object.player1.id
				self.player_2_id = self.match_object.player2.id
			
			if not self.isAi and not self.isLocal:
				# Inizializza o aggiorna la lista dei giocatori per il match corrente
				self.match_manager.inzialize_list_of_players(self.match_id, self.client_id, self)

			if not self.isAi and not self.isLocal:
				# Carica gli oggetti User per entrambi i giocatori
				self.match_manager.add_player(self.match_object.player1)
				self.match_manager.add_player(self.match_object.player2)

			# Configura i binding della tastiera per entrambi i giocatori
			self.keyboard = {
				self.player_1_id: self.match_manager.get_defoult_keyboard(self.player_1_id),
				self.player_2_id: self.match_manager.get_defoult_keyboard(self.player_2_id, self.isLocal)
			}

			self.left_player = Player(
				name = self.player_1_id,
				binds = self.keyboard[self.player_1_id]
			)

			self.right_player = Player(
				name = self.player_2_id,
				binds = self.keyboard[self.player_2_id]
			)

			multipalyer_keyboard = {
				f'up.{self.player_1_id}': False,
				f'down.{self.player_1_id}': False,
				f'up.{self.player_2_id}': False,
				f'down.{self.player_2_id}': False,
			}

			local_keyboard = {
				# Tastiera per giocatore 1
				f'up.{self.client_id}': False,
				f'down.{self.client_id}': False,

				# Tastiera per giocatore 2
				f"w.{self.client_id}": False,
				f"s.{self.client_id}": False,
			}

			# Inizializza la tastiera condivisa del gioco
			Pong.shared_game_keyboard[self.match_id] = multipalyer_keyboard if not self.isLocal else local_keyboard

			Pong.run_game[self.match_id] = False

			# Crea l'oggetto Game condiviso
			Pong.shared_game[self.match_id] = Game(
				dictKeyboard = Pong.shared_game_keyboard[self.match_id],
				leftPlayer = self.left_player,
				rightPlayer = self.right_player,
				scoreLimit = self.scorelimit,
				ia_opponent = self.isAi
			)

		except Exception as e:
			logger.error(f"Error loading models: {e}")
			await self.close()

	@database_sync_to_async
	@transaction.atomic
	def save_models(self, disconnect: bool = False, close_code: int = 1000) -> Optional[Dict[str, Any]]:
		
		if self.isAi:
			game = Pong.shared_game[self.match_id]
			winner = self.player_2_id if game._rightPlayer.score > game._leftPlayer.score else self.player_1_id
			return {
				"winner_id": winner,
				"winner_username": "AI" if winner == self.player_2_id else self.player_object.username,
				"loser_id": "AI" if winner == self.player_1_id else self.player_object.id,

				"player1_username": self.player_object.username,
				"player1_score": game._leftPlayer.score,
				"player2_username": "AI",
				"player2_score": game._rightPlayer.score,
			}
		
		if self.isLocal:
			game = Pong.shared_game[self.match_id]
			winner = self.player_2_id if game._rightPlayer.score > game._leftPlayer.score else self.player_1_id
			return {
				"winner_id": winner,
				"winner_username": "Guest" if winner == self.player_2_id else self.player_object.username,
				"loser_id": "Guest" if winner == self.player_1_id else self.player_object.id,

				"player1_username": self.player_object.username,
				"player1_score": game._leftPlayer.score,
				"player2_username": "Guest",
				"player2_score": game._rightPlayer.score,
			}

		User = import_string('api.authuser.models.CustomUser')

		if Pong.finished.get(self.match_id):
			return

		match_object = self.match_manager.get_match_atomic(self.match_id)
		game = Pong.shared_game[self.match_id]
		player1_id = self.player_1_id
		player2_id = self.player_2_id

		# Aggiorna i punteggi dei giocatori
		match_object.player1_score = game._leftPlayer.score
		match_object.player2_score = game._rightPlayer.score

		# Determina il vincitore
		if disconnect:
			winner_id = player2_id if int(self.client_id) == int(player1_id) else player1_id
		elif match_object.player1_score == match_object.player2_score:
			winner_id = None
		else:
			winner_id = player1_id if match_object.player1_score > match_object.player2_score else player2_id

		match_object.winner = User.objects.get(id=winner_id) if winner_id else None

		# Aggiorna il modello Match
		match_object.date_played = timezone.now()
		match_object.active = False
		match_object.save()

		Pong.finished[self.match_id] = True

		if match_object.winner:
			self.match_manager.update_elo(
				match_object,
				self.player_1_id
			)

			return {
				"winner_id": winner_id,
				"winner_username": match_object.winner.username if match_object.winner else None,
				"loser_id": self.player_1_id if winner_id == player2_id else player2_id,
				"winner_elo": self.match_manager.winner.ELO,
				"loser_elo": self.match_manager.loser.ELO,
				"player1_id": match_object.player1.id,
				"player1_username": match_object.player1.username,
				"player1_score": match_object.player1_score,
				"player2_id": match_object.player2.id,
				"player2_username": match_object.player2.username,
				"player2_score": match_object.player2_score,
			}
		else:
			logger.info(f"Match {self.match_id} ended in a tie.")
