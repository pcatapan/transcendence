from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound
from .jwt_utils import validate_and_get_user_from_token
import logging

# List of paths that should be excluded from token verification
EXCLUDED_PREFIXES = [
	'/api/user/login/',
	'/api/user/signup/',
	'/api/user/validate-jwt/',
	'/api/verify_totp_code/',
	'/api/oauth-init/',
	'/api/oauth/login/'
	'/api/user/exists/',
	'/media/',
	'/pong/',
	'/admin/',
]

logger = logging.getLogger(__name__)

# Determina se il path da cui arriva la richiesta debba essere escluso
def should_exclude_path(request_path):
    return any(request_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)

# Estrae il JWT dall'header
def get_token_from_header(request):
    authorization_header = request.headers.get('Authorization', '')
    if authorization_header.startswith('Bearer '):
        return authorization_header[len('Bearer '):].strip()
    logger.warning('JWT token not found in the Authorization header')
    return None

def error_response(response):
    return JsonResponse({
        'message': str(response.reason_phrase)
    }, status=response.status_code)

# Middleware di verifica del JWT
class JWTVerificationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if should_exclude_path(request.path):
            response = self.get_response(request)
            if isinstance(response, HttpResponseNotAllowed):
                return error_response(response)
            
            return response

        token = get_token_from_header(request)
        if token is None:
            return JsonResponse({
                'error': 'JWT token required'
            }, status=401)

        user = validate_and_get_user_from_token(token)
        if not user:
            logger.warning('Invalid or expired JWT token')
            return JsonResponse({
                'error': 'Invalid or expired token'
            }, status=401)

        request.user = user

        response = self.get_response(request)
        if isinstance(response, HttpResponseNotFound) or isinstance(response, HttpResponseNotAllowed):
            return error_response(response)
        
        return response