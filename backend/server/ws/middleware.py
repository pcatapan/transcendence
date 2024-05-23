from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from api.jwt_utils import validate_and_get_user_from_token

import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token):
    try:
        return validate_and_get_user_from_token(token)
    except Exception as e:
        return AnonymousUser()

class JWTVerificationMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        headers = dict(scope['headers'])
        cookies = headers.get(b'cookie', b'').decode()
        token = None

        for cookie in cookies.split(';'):
            if cookie.strip().startswith('Authorization='):
                token = cookie.strip().split('=')[1]

        scope['user'] = AnonymousUser()
        if token:
            scope['user'] = await get_user_from_token(token)
        
        inner = self.inner
        return await inner(scope, receive, send)