import os
import json

from django.http import JsonResponse

def set_token(user, jwt_token, message):
	response = JsonResponse({
		'message': message,
		'data' : user.to_json()
	}, status=200)

	secure = True if os.getenv('ENVIRONMENT', True) == 'production' else False

	response.set_cookie(
		key='Authorization',
		value=jwt_token,
		httponly=True,
		secure=secure,
		samesite='Strict',
		max_age=os.getenv('JWT_EXPIRATION_TIME', 14400)
	)

	return response