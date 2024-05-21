from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .controllers.user import show, update_avatar, update, user_friends_list, \
	user_friends_add, user_friends_remove, user_blocked_list, user_blocked_add, user_blocked_remove
from .controllers.auth import signup, login
from .controllers.googleauth import enable_2fa, disable_2fa, display_qr_code, verify_totp_code, user_2fa_setup_complete
from .controllers.auth import oauth_start, oauth_login
from .controllers.stats import get_kpi

urlpatterns = [

	path('user/signup', signup, name="signup"),
	path('user/show/<int:user_id>', show, name="user-show"),
	path('user/update', update, name="user-update"),
	path('user/update-avatar', update_avatar, name='update-avatar'),
	path('user/friendlist', user_friends_list, name='user_friendlist'),
	path('user/friend/add/', user_friends_add, name='user_friend_add'),
	path('user/friend/remove/', user_friends_remove, name='user_friend_remove'),
	path('user/blockedlist', user_blocked_list, name='user_blockedlist'),
	path('user/blocked/add/', user_blocked_add, name='user_blocked_add'),
	path('user/blocked/remove/', user_blocked_remove, name='user_blocked_remove'),

	path('user/login', login, name="login"),
	path('enable_2fa', enable_2fa, name='enable_2fa'),
	path('disable_2fa', disable_2fa, name='disable_2fa'),
	path('verify_totp_code', verify_totp_code, name='verify_totp_code'),
	path('display_qr_code', display_qr_code, name='display_qr_code'),
	path('is_2fa_setup_complete', user_2fa_setup_complete, name="is_2fa_setup_complete"),

	path('oauth-init', oauth_start, name="oauth-start"),
	path('oauth/login', oauth_login, name="oauth-login"),

	path('user/stats', get_kpi, name="get_kpi"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)