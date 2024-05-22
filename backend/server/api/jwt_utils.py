import os
from .authuser.jwt.sign import sign
from .authuser.jwt.verify import verify
from .authuser.jwt.decode import decode
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)
    
secret_key = os.environ["JWT_SEED"]

def create_jwt_token(user_id, username):
	now = datetime.now()
	jwt_expiration_time = int(os.getenv('JWT_EXPIRATION_TIME', 14400))
	expiration_time = now + timedelta(seconds=jwt_expiration_time)

	jwt_payload = {
		'user_id': user_id,
		'username': username,
		'expiration': expiration_time.isoformat()
	}

	return sign(jwt_payload, secret_key)

def validate_and_get_user_from_token(token):
	try:
		payload = verify(token, secret_key)
		
		expiration_time_str = payload.get('expiration')
		expiration_time = datetime.fromisoformat(expiration_time_str)
		
		if expiration_time < datetime.now():
			raise Exception('Token has expired', 401)

		user_id = payload.get('user_id')
		
		from api.authuser.models.custom_user import CustomUser

		try:
			user = CustomUser.objects.get(id=user_id)
		except CustomUser.DoesNotExist:
			raise Exception('CustomUser not found', 404)
		
		return {
			'id'        : user.id,
			'username'  : user.username,
			'fullname'  : user.fullname
		}

	except Exception as e:
		raise Exception(e.args[0], e.args[1])
    
def get_user_id_from_jwt(token):
	try:
		payload = verify(token, secret_key)

		expiration_time_str = payload.get('expiration')
		expiration_time = datetime.fromisoformat(expiration_time_str)

		if expiration_time < datetime.now():
			raise Exception('Token has expired', 401)

		user_id = payload.get('user_id')

		return user_id

	except Exception as e:
		raise Exception(e.args[0], e.args[1])