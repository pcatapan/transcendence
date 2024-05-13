import os
import pyotp
import qrcode
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from api.authuser.models.custom_user import CustomUser
from api.jwt_utils import create_jwt_token, get_user_id_from_jwt_token

def generate_secret_key():
	return pyotp.random_base32()

def generate_qr_code(secret_key, user_id):
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    totp = pyotp.TOTP(secret_key)
    uri = totp.provisioning_uri(
        name=f"user_{user_id}", issuer_name="42 Pong")
    
    img = qrcode.make(uri)
    
    img_path = os.path.join(static_folder, f'qrcode_{user_id}.png')
    img.save(img_path)
    
    return img_path


def save_secret_key_in_database(user_id, secret_key):
	user_profile, created = CustomUser.objects.get_or_create(
		id=user_id, defaults={'secret_key': secret_key})

	if not created:
		user_profile.secret_key = secret_key
		user_profile.save()


def get_secret_key_from_database(user_id):
	user_profile = CustomUser.objects.get(id=user_id)

	return user_profile.secret_key


def display_qr_code(request):
	user = get_object_or_404(CustomUser, pk=request.user.id)
		
	if not user.is_2fa_enabled:
		return JsonResponse({'message': '2FA is already disabled.'}, status=400)

	secret_key = generate_secret_key()
	img_path = generate_qr_code(secret_key, user_id)
	user.enable_2fa(secret_key)

	return JsonResponse({'qrcode_path': img_path, 'user_id': user_id}, status=200)

def enable_2fa(request):
	user = get_object_or_404(CustomUser, pk=request.user.id)

	print("enable secret key: ", user.secret_key)
	if user.is_2fa_enabled:
		return JsonResponse({'message': '2FA is already enabled.'}, status=200)

	secret_key = pyotp.random_base32()
	img_path = generate_qr_code(secret_key, user.id)
	user.enable_2fa(secret_key)

	return JsonResponse({
			'qrcode_path': img_path,
			'message': 'Scan the QR code with your authenticator app to enable 2FA.'
		},
		status=200
	)

def disable_2fa(request):
	user = get_object_or_404(CustomUser, pk=request.user.id)

	if not user.is_2fa_enabled:
		return JsonResponse({'message': '2FA is already disabled.'}, status=200)

	user.disable_2fa()
	return JsonResponse({'message': '2FA has been disabled.'}, status=200)

@require_POST
def verify_totp_code(request):

	try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': "Invalid JSON"}, status=400)

	try:
		user_id = data.get('user_id')
		totp_code = data.get('totp_code')
		
		uuser = get_object_or_404(CustomUser, pk=user_id)

		if not user.is_2fa_enabled:
			return JsonResponse({'message': '2FA is not enabled for this user.'}, status=400)
		
		print("secret key: ", user.secret_key)
		totp = pyotp.TOTP(user.secret_key)
		is_valid = totp.verify(totp_code)

		print("secret key: ", user.secret_key)
		print("Is valid: ", is_valid)

		if is_valid:
			user.is_2fa_setup_complete = True
			user.save()

			jwt_token = create_jwt_token(user.id, user.username)
			return JsonResponse({'message': 'TOTP is valid', 'token': jwt_token}, status=200)
		else:
			return JsonResponse({'message': 'Invalid TOTP'}, status=400)

	except pyotp.OTPError as e:
		return JsonResponse({'message': f'Error: {str(e)}'}, status=400)

@require_GET
def user_2fa_setup_complete(request):
	user = get_object_or_404(CustomUser, pk=request.user.id)

	try:
		if user.is_2fa_enabled and user.is_2fa_setup_complete:
			return JsonResponse({'status': True}, status=200)
		return JsonResponse({'status': False}, status=200)

	except CustomUser.DoesNotExist:
		return JsonResponse({'message': 'User not found'}, status=400)
