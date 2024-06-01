import json
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
from .. import constants

logger = logging.getLogger(__name__)

def set_frame_rate(fps):
	if fps < 1 or fps > 60 or not isinstance(fps, int):
		fps = 60
	return 1 / fps

class Pong(AsyncWebsocketConsumer, Message):
	match_manager = MatchManager()

	shared_game_keyboard = {}
	shared_game_task = {}
	shared_game = {}
	run_game = {}
	finished = {}
	scorelimit = 10

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
			#self.room_group_name = f'match_{self.match_id}'

			self.match_object = await self.match_manager.get_match_and_player(self.match_id)
			if not self.match_object:
				await self.close()
				return
			
			if user.id not in {self.match_object.player1.id, self.match_object.player2.id}:
				logger.info(f"User {self.client_id} is in the match {self.match_id}")
				await self.close()
				return

			if self.match_object.active:
				logger.error(f"Match {self.match_id} is active")
				await self.close()
				return

			logger.info(f"Adding client {self.client_id} to the match {self.match_id}")

			await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
			# da valutare se serve
			await self.channel_layer.group_add(f"{self.match_id}.player.{self.client_id}", self.channel_name)

			logger.info(f"loading models for match {self.match_id}")
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
			
			logger.info(f"Checking if both players are connected to the match {self.match_id}")
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
			logger.info(f"Client {self.client_id} connected")
				  
		except Exception as e:
			await self.close()
			logger.error(f"Error during connect: {e}")

	async def disconnect(self, code=1000):

		logger.info(f"Client {self.client_id} disconnected with code {code}")
		if (code == 4001 or self.match_id is None):
			return

		if self.match_manager.player_in_list(self.client_id, self.match_id):
			self.match_manager.remove_player(self.match_id, self.client_id)

		Pong.run_game[self.match_id] = False
		await self.check_reconnect()

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
		logger.info('receive')
		logger.info(f"Text data: {text_data}")
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
			await self.send_json({'error': 'Game not started'})
			return

		try:
			key_status = data.get('key_status')
			key = data.get('key')
			formatted_key = f'{key}.{self.client_id}'

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
		Pong.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(data))

# -------------------------------------------------------------------------------------




# -------------------------------------- Methods ----------------------------------------
	async def load_models(self):
		try:
			self.player_1_id = str(self.match_object.player1.id)
			self.player_2_id = str(self.match_object.player2.id)

			# Inizializza o aggiorna la lista dei giocatori per il match corrente
			self.match_manager.inzialize_list_of_players(self.match_id, self.client_id, self)

			# Carica gli oggetti User per entrambi i giocatori
			self.match_manager.add_player(self.match_object.player1)
			self.match_manager.add_player(self.match_object.player2)

			# Configura i binding della tastiera per entrambi i giocatori
			self.keyboard = {
				self.player_1_id: self.match_manager.get_defoult_keyboard(self.player_1_id),
				self.player_2_id: self.match_manager.get_defoult_keyboard(self.player_2_id),
			}

			self.left_player = Player(
				name = self.player_1_id,
				binds = self.keyboard[self.player_1_id]
			)
			self.right_player = Player(
				name = self.player_2_id,
				binds = self.keyboard[self.player_2_id]
			)

			# Inizializza la tastiera condivisa del gioco
			Pong.shared_game_keyboard[self.match_id] = {
				f'up.{self.player_1_id}': False,
				f'down.{self.player_1_id}': False,
				f'up.{self.player_2_id}': False,
				f'down.{self.player_2_id}': False,
			}

			Pong.run_game[self.match_id] = False

			# Crea l'oggetto Game condiviso
			Pong.shared_game[self.match_id] = Game(
				dictKeyboard = Pong.shared_game_keyboard[self.match_id],
				leftPlayer = self.left_player,
				rightPlayer = self.right_player,
				scoreLimit = self.scorelimit,
			)

		except Exception as e:
			logger.error(f"Error loading models: {e}")
			await self.close()
	
	@database_sync_to_async
	@transaction.atomic
	def save_models(self, disconnect: bool = False, close_code: int = 1000) -> Optional[Dict[str, Any]]:
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

	async def async_proces_game(self, data):
		try:
			frame_rate = set_frame_rate(60)
			match_id = self.match_id
			game = Pong.shared_game[match_id]

			while Pong.run_game[match_id]:
				game.pointLoop()

				left_score = game._leftPlayer.score
				right_score = game._rightPlayer.score

				if left_score >= self.scorelimit or right_score >= self.scorelimit:
					Pong.run_game[match_id] = False
					await self.broadcast_layer(
						await self.save_models(),
						str(match_id),
						constants.FINISH_MATCH,
						priority='high',
					)
					Pong.finished[match_id] = True

					await asyncio.sleep(0.5)
					await self.close()

					return

				await self.broadcast_layer(
					{
						"canvas": game.reportScreen(),
						"left_score": left_score,
						"right_score": right_score
					},
					str(match_id),
					constants.UPDATE_GAME,
				)
				await asyncio.sleep(frame_rate)

			await asyncio.sleep(0.5)

			if Pong.finished[match_id]:
				await self.close()

		except asyncio.CancelledError:
			logger.info('Game stopped')
		except Exception as e:
			logger.error(f"Error during aync_proces_game: {e}")
			await self.close()
	
	async def check_reconnect(self):
		try:
			for seconds in range(constants.SECOND_WAIT):
				await self.broadcast_layer(
					{
						"message": "Waiting for opponent to reconnect",
						"seconds_left": f"{constants.SECOND_WAIT - seconds - 1} seconds"
					},
					str(self.match_id),
					constants.WAITING_FOR_OPPONENT,
				)
				await asyncio.sleep(1)

				if len(self.match_manager.list_of_players(self.match_id)) == 2:
					logger.info(f"Both players reconnected in match {self.match_id}. Resuming game.")
					Pong.run_game[self.match_id] = True
					Pong.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(None))
					return

			# If the loop completes without both players reconnecting, close the match
			logger.info(f"Opponent did not reconnect within the time limit for match {self.match_id}. Closing match.")
			await self.close()

		except Exception as e:
			logger.error(f"Error during check_reconnect: {e}")
			await self.close()

	async def discard_channels(self):
		try:
			await self.channel_layer.group_discard(
				f"{self.match_id}",
				self.channel_name
			)
			await self.channel_layer.group_discard(
				f"{self.match_id}.player.{self.player_1_id}",
				self.channel_name
			)
			await self.channel_layer.group_discard(
				f"{self.match_id}.player.{self.player_2_id}",
				self.channel_name
			)
			
		except Exception as e:
			logger.error(f"Error during discard_channels: {e}")
			await self.close()
