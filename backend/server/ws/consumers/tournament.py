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
from .. import constants

logger = logging.getLogger(__name__)

def set_frame_rate(fps):
	if fps < 1 or fps > 60 or not isinstance(fps, int):
		fps = constants.BASE_FPS
	return 1 / fps

class Tournament(AsyncWebsocketConsumer, Message):
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

		if self.match_manager.player_in_list(self.client_id, self.match_id):
			self.match_manager.remove_player(self.match_id, self.client_id)

		Tournament.run_game[self.match_id] = False

		if not Tournament.finished[self.match_id]:
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

	async def load_models(self):
		try:

			self.player_1_id = self.match_object.player1.id
			self.player_2_id = self.match_object.player2.id

			self.match_manager.inzialize_list_of_players(self.match_id, self.client_id, self)
			self.match_manager.add_player(self.match_object.player1)
			self.match_manager.add_player(self.match_object.player2)

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
				f'up.{self.client_id}': False,
				f'down.{self.client_id}': False,
				f"w.{self.client_id}": False,
				f"s.{self.client_id}": False,
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
		if self.isLocal:
			game = Tournament.shared_game[self.match_id]
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

		if Tournament.finished.get(self.match_id):
			return

		match_object = self.match_manager.get_match_atomic(self.match_id)
		game = Tournament.shared_game[self.match_id]
		player1_id = self.player_1_id
		player2_id = self.player_2_id

		match_object.player1_score = game._leftPlayer.score
		match_object.player2_score = game._rightPlayer.score

		if disconnect:
			winner_id = player2_id if int(self.client_id) == int(player1_id) else player1_id
		elif match_object.player1_score == match_object.player2_score:
			winner_id = None
		else:
			winner_id = player1_id if match_object.player1_score > match_object.player2_score else player2_id

		match_object.winner = User.objects.get(id=winner_id) if winner_id else None
		match_object.date_played = timezone.now()
		match_object.active = False
		match_object.save()

		Tournament.finished[self.match_id] = True

		if match_object.winner:
			self.match_manager.update_elo(match_object, self.player_1_id)

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
			frame_rate = set_frame_rate(constants.BASE_FPS)
			match_id = self.match_id
			game = Tournament.shared_game[match_id]
			start_time = time.time()

			prev_state = None

			while Tournament.run_game[match_id]:
				game.pointLoop()

				left_score = game._leftPlayer.score
				right_score = game._rightPlayer.score
				elapsed_time = time.time() - start_time

				current_state = {
					"canvas": game.reportScreen(),
					"left_score": left_score,
					"right_score": right_score,
					"elapsed_time": elapsed_time
				}

				if left_score >= self.scorelimit or right_score >= self.scorelimit:
					Tournament.run_game[match_id] = False
					await self.broadcast_layer(
						current_state,
						str(match_id),
						constants.UPDATE_GAME,
					)

					await self.broadcast_layer(
						await self.save_models(),
						str(match_id),
						constants.FINISH_MATCH,
						priority='high',
					)
					Tournament.finished[match_id] = True

					await asyncio.sleep(0.5)
					await self.close_with_timeout()
					return
				
				if prev_state != current_state:
					await self.broadcast_layer(
						current_state,
						str(match_id),
						constants.UPDATE_GAME,
					)
					await asyncio.sleep(frame_rate)
					prev_state = current_state

			await asyncio.sleep(1)

			if Tournament.finished[match_id]:
				await self.close_with_timeout()

		except asyncio.CancelledError:
			logger.info('Game stopped')
		except Exception as e:
			logger.error(f"Error during aync_proces_game: {e}")
			await self.close_with_timeout()

	async def check_reconnect(self):
		try:
			for seconds in range(constants.SECOND_WAIT):
				try:
					await self.broadcast_layer(
						{
							"message": "Waiting for opponent to reconnect",
							"seconds_left": f"{constants.SECOND_WAIT - seconds - 1} seconds"
						},
						str(self.match_id),
						constants.WAITING_FOR_OPPONENT,
					)
					await asyncio.sleep(1)
				except Exception as e:
					logger.error(f"Error during check_reconnect - broadcast_layer: {e}")
					return

				try:
					if len(self.match_manager.list_of_players[self.match_id]) == 2:
						logger.info(f"Both players reconnected in match {self.match_id}. Resuming game.")
						Tournament.run_game[self.match_id] = True
						Tournament.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(None))
						return
				except Exception as e:
					logger.error(f"Error during check_reconnect - list_of_players: {e}")
					return

			logger.info(f"Opponent did not reconnect within the time limit for match {self.match_id}. Closing match.")
			await self.close()

		except Exception as e:
			logger.error(f"Error during check_reconnect: {e}")
			await self.close()

	async def close_with_timeout(self, code=1000):
		try:
			await asyncio.wait_for(self.close(code), timeout=5)
		except asyncio.TimeoutError:
			logger.warning("Closing the WebSocket took too long and was forcefully terminated.")

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
