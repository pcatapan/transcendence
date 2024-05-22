from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from channels.db import database_sync_to_async

from api.jwt_utils import get_user_id_from_jwt

import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.online_users = {}

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            user_id = get_user_id_from_jwt(token)
            return str(user_id)
        except Exception as e:
          None

    @database_sync_to_async
    def add_user_to_lobby(self, user_id, channel_name):
        User = import_string('api.authuser.models.CustomUser')
        user = get_object_or_404(User, pk=user_id)
        
        try :
            self.online_users[user_id] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'channel': channel_name
            }
        except Exception as e:
            logger.error(f"Error adding user to lobby: {e}")

    async def remove_user_from_lobby(self, user_id):
        if user_id in self.online_users:
            del self.online_users[user_id]

    def list_online_users(self):
        return self.online_users

    async def send_private_message(self, recipient_id, message):
        channel_name = self.online_users.get(recipient_id, {}).get('channel')
        logger.info(f"Sending private message to user with ID {recipient_id}")
        logger.info(f"Channel name: {channel_name}")
        if channel_name:
            try:
                await self.channel_layer.send(channel_name, {
                    'type': 'private_message',
                    'message': {
                        'timestamp': timezone.now().isoformat(),
                        'sender': self.client_id,
                        'content': message,
                    }
                })
                logger.info(f"Sent private message to user with ID {recipient_id}")
            except Exception as e:
                logger.error(f"Error sending private message to user with ID {recipient_id}: {e}")
        else:
            logger.warning(f"User with ID {recipient_id} is not online")
