import os
import json
import pyotp
import qrcode
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404

from .validation.user_validator import UserStoreValidator
from api.authuser.oauth.user import get_user_info, get_or_create_user_oauth
from api.authuser.models.custom_user import CustomUser
from api.jwt_utils import create_jwt_token

@require_POST
def signup(request):
	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': "Invalid JSON"}, status=400)

	input_errors = UserStoreValidator(data).validate()
	if input_errors:
		return JsonResponse({"message": "Something went wrong", "details": input_errors}, status=403)

	user = CustomUser(username=username, fullname=fullname, email=email)
	user.set_password(password)
	
	user.save()
	jwt_token = create_jwt_token(user.id, user.username)
	response = JsonResponse({'message': 'User created successfully', 'token': jwt_token})

	return response


@require_POST
def login(request):
	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': "Invalid JSON"}, status=400)

	username = data.get('username')
	password = data.get('password')

	user = CustomUser.objects.get(username=username)
	
	if user.check_password(password):
		if user.is_2fa_enabled and user.is_2fa_setup_complete:
			response = JsonResponse({'status': '2FA', 'message': 'Login successful', 'user_id': user.id}, status=200)
		else:
			jwt_token = create_jwt_token(user.id, user.username)
			response = JsonResponse({'message': 'Login successful', 'token': jwt_token}, status=200)

		return response
	else:
		return JsonResponse({'message': 'Invalid credentials'}, status=401)


def oauth_start(request):
    client_id = os.getenv("INTRA_CLIENT_ID")
    redirect_uri = os.getenv("INTRA_REDIRECT_URI")
    oauth_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    
    response = JsonResponse({'url': oauth_url}, status=200)
    response['Access-Control-Allow-Methods'] = '*'
    response['Access-Control-Allow-Headers'] = '*'

    return response

@require_POST
def oauth_login(request):

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': "Invalid JSON"}, status=400)
	
	code = data.get("code")
	if not code:
		return JsonResponse({"detail": "No code provided"}, status=400)

	data = {
		"client_id": os.getenv("INTRA_CLIENT_ID"),
		"client_secret": os.getenv("INTRA_CLIENT_SECRET"),
		"redirect_uri": os.getenv("INTRA_REDIRECT_URI"),
		"grant_type": "authorization_code",
		"code": code,
	}

	oauth_url = "https://api.intra.42.fr/oauth/token/"

	response = requests.post(oauth_url, json=data)
	if response.status_code != 200:
		return JsonResponse({"detail": "Invalid code"}, status=401)

	access_token = response.json().get("access_token")
	user_info = get_user_info(access_token)

	user = get_or_create_user_oauth(user_info)
	jwt_token = create_jwt_token(user.id, user.username)

	return JsonResponse({"token": jwt_token})