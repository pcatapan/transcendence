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
    
    def get_user_channel(self, user_id):
        logger.info(f"Online users: {self.online_users}")
        logger.info(f"User {self.online_users.get(user_id, {})}")
        return self.online_users.get(user_id, {}).get('channel')
    
    def get_user(self, user_id):
        return self.online_users.get(user_id, {})
