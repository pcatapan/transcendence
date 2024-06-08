# constants.py

# Constants
LOBBY_NAME = 'lobby'
GAME_NAME = 'game'
ELO_DIFF = 300
ELO_BASE = 25
ELO_MOLTIPLIER = 2.5
SECOND_WAIT = 10
AI_PREFIX_MATCH = '_vs_ia_'
LOCAL_PREFIX_MATCH = '_vs_local_'
AI_REACTION = 0.03
BASE_FPS = 60
SCORE_LIMIT = 10

# Endpoints and commands (Client -> Server)
# LOBBY
LIST_OF_USERS = 'list_of_users'
SEND_PRV_MSG = 'send_prv_msg'
JOIN_QUEUE = 'join_queue'
LEAVE_QUEUE = 'leave_queue'
FOUND_OPPONENT = 'found_opponent'
CONFIRM_MATCH = 'confirm_match'
IA_OPPONENT = 'ia_opponent'
IA_FOUND = 'ia_found'
LOCAL_OPPONENT = 'local_opponent'
LOCAL_FOUND = 'local_found'
# END LOBBY

# GAME
KEYBOARD = 'keyboard'
START_BALL = 'start_ball'
UPDATE_GAME = 'update_game'
FINISH_MATCH = 'finish_match'
WAITING_FOR_OPPONENT = 'waiting_for_opponent'
CONNECTED_USERS = 'connected_users'
# END GAME 