from django.utils import timezone
import json
import logging
from .. import constants

logger = logging.getLogger(__name__)

class Message:
	async def broadcast_layer(self, content, channel, command=None, type='broadcast', priority='normal', status='200'):
		if channel is None:
			return
		
		message = {
			'status': status,
			'type' : type,
			'content': content,
			'command': command,
			'timestamp': timezone.now().isoformat(),
			'meta': {
				"priority": priority,
			}
		}

		try:
			await self.channel_layer.group_send(channel, message)
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
				'next_command': event['next_command'],
				'sender': sender,
				'timestamp': timezone.now().isoformat(),
				'meta': event['meta']
			})
		except Exception as e:
			logging.error(f"Error in unicast method: {e}")
	
	async def send_layer(self, content, command=None, type="inform", priority='normal', status='200', channel='lobby'):
		try:
			await self.send_json({
				'status': status,
				'type': type,
				'command': command,
				'content': content,
				'timestamp': timezone.now().isoformat(),
				'meta': {
					"channel": channel,
					"priority": priority,
				}
			})
		except Exception as e:
			logging.error(f"Error in send_layer method: {e}")

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

