import os
import pyotp
import qrcode
import json
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from api.authuser.models.custom_user import CustomUser
from api.jwt_utils import create_jwt_token, get_user_id_from_jwt_token

def generate_secret_key():
	return pyotp.random_base32()

def generate_qr_code(secret_key, user):
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    totp = pyotp.TOTP(secret_key)
    uri = totp.provisioning_uri(
        name=f"{user.username}", issuer_name="42 Pong")
    
    img = qrcode.make(uri)
    
    img_path = os.path.join(static_folder, f'qrcode_{user.id}.png')
    img.save(img_path)
    
    return img_path

@require_GET
def display_qr_code(request):
	user = get_object_or_404(CustomUser, pk=request.user['id'])
		
	if not user.is_2fa_enabled:
		return JsonResponse({
			'message': '2FA is already disabled.'
		}, status=400)

	secret_key = generate_secret_key()
	img_path = generate_qr_code(secret_key, user)
	user.enable_2fa(secret_key)

	return JsonResponse({
		'callback': reverse('verify_totp_code'),
		'message': 'Scan the QR code with your authenticator app to enable 2FA.',
		'data' : {
			'img_path': img_path,
			'user_id': user.id
		}
	}, status=206)

@require_POST
def enable_2fa(request):
	user = get_object_or_404(CustomUser, pk=request.user['id'])

	print("enable secret key: ", user.secret_key)
	if user.is_2fa_enabled:
		return JsonResponse({
			'message': '2FA is already enabled.'
		}, status=200)

	secret_key = pyotp.random_base32()
	img_path = generate_qr_code(secret_key, user)
	user.enable_2fa(secret_key)

	return JsonResponse({
			'callback': reverse('verify_totp_code'),
			'message': 'Scan the QR code with your authenticator app to enable 2FA.',
			'data': img_path
		}, status=206)

@require_POST
def disable_2fa(request):
	user = get_object_or_404(CustomUser, pk=request.user['id'])

	if not user.is_2fa_enabled:
		return JsonResponse({
			'message': '2FA is already disabled.'
		}, status=200)

	user.disable_2fa()
	return JsonResponse({
		'message': '2FA has been disabled.'
	}, status=200)

@require_POST
def verify_totp_code(request):

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({
			'message': "Invalid JSON"
		}, status=400)
	
	if 'user_id' not in data or 'totp_code' not in data:
		return JsonResponse({
			'message': 'Missing user_id or totp_code'
		}, status=400)

	try:
		totp_code = data.get('totp_code')
		
		user = get_object_or_404(CustomUser, pk=data.get('user_id'))

		if not user.is_2fa_enabled:
			return JsonResponse({
				'message': '2FA is not enabled for this user.'
			}, status=400)
		
		print("secret key: ", user.secret_key)
		totp = pyotp.TOTP(user.secret_key)
		is_valid = totp.verify(totp_code)

		print("secret key: ", user.secret_key)
		print("Is valid: ", is_valid)

		if is_valid:
			user.is_2fa_setup_complete = True
			user.save()

			jwt_token = create_jwt_token(user.id, user.username)
			return JsonResponse({
				'message': 'TOTP is valid',
				'token': jwt_token,
				'data' : user.to_json()
			}, status=200)
		else:
			return JsonResponse({
				'message': 'Invalid TOTP'
			}, status=400)

	except pyotp.OTPError as e:
		return JsonResponse({
			'message': f'Error: {str(e)}'
		}, status=400)

@require_GET
def user_2fa_setup_complete(request):
	user = get_object_or_404(CustomUser, pk=request.user['id'])

	try:
		if user.is_2fa_enabled and user.is_2fa_setup_complete:
			return JsonResponse({
				'status': True
			}, status=200)
		return JsonResponse({
			'status': False
		}, status=200)

	except CustomUser.DoesNotExist:
		return JsonResponse({
			'message': 'User not found'
		}, status=400)
