# ws_api/routing.py

from django.urls import re_path
from .consumers.lobby import Lobby
from .consumers.pong import Pong
#from .controllers.tournament import Tournament
#from .controllers.game import Pong

websocket_urlpatterns = [
	re_path(r"^ws/lobby", Lobby.as_asgi()),
	re_path(r"^ws/pong/(?P<match_id>\w+)", Pong.as_asgi(), name='pong'),

	#re_path(r"^ws/tournament/(?P<tournament_id>\w+)/$", Tournament.as_asgi()),
	#re_path(r"^ws/pong/(?P<match_id>\w+)/$", Pong.as_asgi()),
]