import os
import json
import logging
import requests
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404

from .validation.user_validator import UserStoreValidator
from api.authuser.oauth.user import get_user_info, get_or_create_user_oauth
from api.authuser.models.friendship import Friendship
from api.authuser.models.custom_user import CustomUser
from api.jwt_utils import create_jwt_token, get_token, validate_and_get_user_from_token
from .utils.general import set_token

logger = logging.getLogger(__name__)

@require_POST
def signup(request):

	if not request.body:
		return JsonResponse({
			'message': 'Empty payload'
		}, status=400)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({
			'message': "Invalid JSON"
		}, status=400)

	input_errors = UserStoreValidator(data).validate()
	if input_errors:
		return JsonResponse({
			"message": [f"{field}: {error}" for field, error in input_errors.items()],
			"details": input_errors
		}, status=400)

	user = CustomUser(username=data['username'], fullname=data['fullname'], email=data['email'])
	user.set_password(data['password'])
	
	user.save()
	Friendship.objects.create(user=user)
	jwt_token = create_jwt_token(user.id, user.username)

	return set_token(user, jwt_token, 'User created successfully')


@require_POST
def login(request):

	if not request.body:
		return JsonResponse({
			'message': 'Empty payload'
		}, status=400)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({
			'message': "Invalid JSON"
		}, status=400)

	email = data.get('email')
	password = data.get('password')

	user = get_object_or_404(CustomUser, email=email)
	
	if user.check_password(password):
		if user.is_2fa_enabled and user.is_2fa_setup_complete:
			response = JsonResponse({
				'callback': reverse('verify_totp_code'),
				'message': 'Login successful',
				'data': user.id
			}, status=206)
		else:
			jwt_token = create_jwt_token(user.id, user.username)

			response = set_token(user, jwt_token, 'Login successful')

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
		return JsonResponse({
			'message': "Invalid JSON"
		}, status=400)
	
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

	return set_token(user, jwt_token, 'Login successful')

@require_GET
def authenticate(request):
	token = get_token(request)
	if token is None:
		return JsonResponse({}, status=401)
	
	try :
		request.user = validate_and_get_user_from_token(token)
	except Exception as e:
		logger.warning(f'Error validating token: {str(e)}')
		logger.warning(e)

		return JsonResponse({}, status=e.args[1] if len(e.args) > 1 else 401)
	
	return JsonResponse({},status=201)

@require_GET
def logout(request):
	response = JsonResponse({
		'message': 'Logged out successfully'
	}, status=200)

	response.delete_cookie('Authorization')
	return response