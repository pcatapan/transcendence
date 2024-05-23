from ..manager.queue_manager import QueueManager
from ..manager.user_manager import UserManager
from ..manager.tournament_manager import TournamentManager
from .. import constants

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

import json                                                 # Used to encode and decode JSON data
import logging                                              # Used to log errors

logger = logging.getLogger(__name__)

class Lobby(AsyncWebsocketConsumer):
	queue_manager = QueueManager()
	user_manager = UserManager()
	tournament_manager = TournamentManager()

	async def connect(self):
		logger.info('connect')
		try:
			self.client_id = None
			user = self.scope['user']
			if user.is_authenticated:
				self.client_id = str(user.id)
				await self.accept()
			else:
				await self.close()
			
			#check if user is already connected
			if self.client_id in self.user_manager.online_users:
				await self.send_layer({
					'message': 'User already connected',
				}, status='400')
				await self.close(code=4001)
				return

			await self.user_manager.add_user_to_lobby(self.client_id, self.channel_name)
			logger.info(f"User {self.client_id} connected to the lobby")
			logger.info(f"Online users: {self.user_manager.list_online_users()}")
			await self.channel_layer.group_add(constants.LOBBY_NAME, self.channel_name)

			await self.send_layer("Correctly connected to the lobby")

			await self.broadcast_layer({
				'message': f"User {self.client_id} connected to the lobby",
				'users': self.user_manager.list_online_users()
			})

		except Exception as e:
			logger.error(f"Exception during connection: {e}")
			await self.close()

	async def disconnect(self, close_code):
		logger.info('disconnect')
		logger.info(f"Close code: {close_code}")

		if close_code == 4001:
			return

		try:
			if self.client_id:
				await self.user_manager.remove_user_from_lobby(self.client_id)
				await self.broadcast_layer({
				'message': f"User {self.client_id} disconnected from the lobby",
				'users': self.user_manager.list_online_users()
			})
				await self.channel_layer.group_discard(constants.LOBBY_NAME, self.channel_name)
		except Exception as e:
			logger.error(f"Error in disconnect method: {e}")

	async def receive(self, text_data):
		logger.info('receive')
		logger.info(f"Text data: {text_data}")
		try:
			data = json.loads(text_data)
			command = data.get('command')

			handlers = {
				constants.LIST_OF_USERS: self.handle_list_of_users,
				constants.SEND_PRV_MSG: self.handle_send_prv_msg,

				constants.JOIN_QUEUE: self.handle_join_queue,
				constants.LEAVE_QUEUE: self.handle_leave_queue,

				constants.CREATE_3v3: self.handle_create_tournament,
				constants.JOIN_3v3: self.handle_join_tournament,
				constants.START_3v3: self.handle_start_tournament,
			}

			handler = handlers.get(command, self.handle_unknown_command)
			await handler(data)
		except json.JSONDecodeError as e:
			logger.error(f"JSON decode error: {e}")
		except Exception as e:
			logger.error(f"Error in receive method: {e}")

# -------------------------------------------------------------------------------------




# ---------------------------------Messaging methods-----------------------------------

	async def broadcast_layer(self, content, command=None, type='broadcast', priority='normal', status='200'):

		message = {
			'status': status,
			'type' : type,
			'content': content,
			'command': command,
			'timestamp': timezone.now().isoformat(),
			'meta': {
				"channel": "lobby",
				"priority": priority,
			}
		}

		try:
			await self.channel_layer.group_send(constants.LOBBY_NAME, message)
		except Exception as e:
			logging.error(f"Error in broadcast_layer method: {e}")
	
	async def unicast(self, event):
		sender = self.user_manager.get_user(self.client_id)

		try:
			await self.send_json({
				'status': event['status'],
				'type': 'unicast',
				'command' : event['command'],
				'content': event['content'],
				'sender': sender,
				'timestamp': timezone.now().isoformat(),
				'meta': event['meta']
			})
		except Exception as e:
			logging.error(f"Error in unicast method: {e}")
	
	async def send_layer(self, content, command=None, type="inform", priority='normal', status='200'):
		try:
			await self.send_json({
				'status': status,
				'type': type,
				'command': command,
				'content': content,
				'timestamp': timezone.now().isoformat(),
				'meta': {
					"channel": "lobby",
					"priority": priority,
				}
			})
		except Exception as e:
			logging.error(f"Error in inform method: {e}")

	async def broadcast(self, event):
		try:
			await self.send_json({
				'status': event['status'],
				'type': 'broadcast',
				'command': event['command'],
				'content': event['content'],
				'timestamp': timezone.now().isoformat(),
				'meta': event['meta']
			})
		except Exception as e:
			logging.error(f"Error in broadcast method: {e}")

	async def send_json(self, message):
		await self.send(text_data=json.dumps(message))

# -------------------------------------------------------------------------------------




# -------------------------------------- Handle ----------------------------------------
	async def handle_list_of_users(self, data):
		await self.send_layer(
			self.user_manager.list_online_users(),
			type=constants.LIST_OF_USERS,
			command=constants.LIST_OF_USERS
		)

	async def handle_send_prv_msg(self, data):
		recipient_channel_name = self.user_manager.get_user_channel(str(data['recipient_id']))

		try:
			await self.channel_layer.send(recipient_channel_name, {
				'status': 200,
				'type': "unicast",
				'command': 'private_message',
				'content': data['message'],
				'meta': {
					"channel": "lobby",
					"priority": 'normal',
				}
			})
		except Exception as e:
			logging.error(f"Error in unicast method: {e}")

	async def handle_join_queue(self, data):
		await self.queue_manager.join_queue(data['queue_name'], self.client_id)

	async def handle_leave_queue(self, data):
		await self.queue_manager.leave_queue(data['queue_name'], self.client_id)

	async def handle_create_tournament(self, data):
		await self.tournament_manager.create_tournament(self.client_id, data['tournament_name'])

	async def handle_join_tournament(self, data):
		await self.tournament_manager.join_tournament(self.client_id)

	async def handle_start_tournament(self, data):
		await self.tournament_manager.start_tournament(self.client_id)

	async def handle_unknown_command(self, data):
		await self.send_json({'error': 'Unknown command'})

# -------------------------------------------------------------------------------------


# WebSocket close codes

# | Close code (uint16) | Codename               | Internal | Customizable | Description |
# |---------------------|------------------------|----------|--------------|-------------|
# | 0 - 999             |                        | Yes      | No           | Unused |
# | 1000                | `CLOSE_NORMAL`         | No       | No           | Successful operation / regular socket shutdown |
# | 1001                | `CLOSE_GOING_AWAY`     | No       | No           | Client is leaving (browser tab closing) |
# | 1002                | `CLOSE_PROTOCOL_ERROR` | Yes      | No           | Endpoint received a malformed frame |
# | 1003                | `CLOSE_UNSUPPORTED`    | Yes      | No           | Endpoint received an unsupported frame (e.g. binary-only endpoint received text frame) |
# | 1004                |                        | Yes      | No           | Reserved |
# | 1005                | `CLOSED_NO_STATUS`     | Yes      | No           | Expected close status, received none |
# | 1006                | `CLOSE_ABNORMAL`       | Yes      | No           | No close code frame has been receieved |
# | 1007                | *Unsupported payload*  | Yes      | No           | Endpoint received inconsistent message (e.g. malformed UTF-8) |
# | 1008                | *Policy violation*     | No       | No           | Generic code used for situations other than 1003 and 1009 |
# | 1009                | `CLOSE_TOO_LARGE`      | No       | No           | Endpoint won't process large frame |
# | 1010                | *Mandatory extension*  | No       | No           | Client wanted an extension which server did not negotiate |
# | 1011                | *Server error*         | No       | No           | Internal server error while operating |
# | 1012                | *Service restart*      | No       | No           | Server/service is restarting |
# | 1013                | *Try again later*      | No       | No           | Temporary server condition forced blocking client's request |
# | 1014                | *Bad gateway*          | No       | No           | Server acting as gateway received an invalid response |
# | 1015                | *TLS handshake fail*   | Yes      | No           | Transport Layer Security handshake failure |
# | 1016 - 1999         |                        | Yes      | No           | Reserved for later |
# | 2000 - 2999         |                        | Yes      | Yes          | Reserved for websocket extensions |
# | 3000 - 3999         |                        | No       | Yes          | Registered first come first serve at IANA |
# | 4000 - 4999         |                        | No       | Yes          | Available for applications |