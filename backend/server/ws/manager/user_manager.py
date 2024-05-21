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
    def add_user_to_lobby(self, user_id):
        User = import_string('api.authuser.models.CustomUser')
        user = get_object_or_404(User, pk=user_id)
        
        self.online_users[user_id] = user.username

    async def remove_user_from_lobby(self, user_id):
        if user_id in self.online_users:
            del self.online_users[user_id]

    def list_online_users(self):
        return self.online_users

    async def send_private_message(self, recipient_id, message):
        # Implement the logic to send a private message to a specific user
        pass
