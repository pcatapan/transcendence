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

LIST_SENT_INVITES = 'list_sent_invites'             # Command to send the list of invites sent
LIST_RECEIVED_INVITES = 'list_received_invites'     # Command to send the list of invites received
SEND_NOTIFICATION = 'send_notification'             # Command to send a group wide notification arguments: pass the values as of 'message' eg: {'command': 'send_notification', 'data': {'message': 'Hello'}}
CMD_NOT_FOUND = 'command_not_found'                 # Command to send when a command is not found
CLOSE_CONNECTION = 'close_connection'               # Command to close the connection
CREATE_USER = 'create_user'                         # Command to create a user arguments: pass the values as of 'user_data'
MODIFY_USER = 'modify_user'                         # Command to modify a user arguments: pass the values as of 'changes'
SERVER_TIME = 'server_time'                         # Command to send the server time
INVITE_TO_MATCH = 'invite_to_match'                 # Command to invite a user to a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'invite_to_match', 'data': {'client_id': '1', 'match_id': '1'}}
REJECT_MATCH = 'reject_match'                       # Command to reject a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'reject_match', 'data': {'client_id': '1', 'match_id': '1'}}
CANCEL_MATCH = 'cancel_match'                       # Command to cancel a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'cancel_match', 'data': {'client_id': '1', 'match_id': '1'}}
SEND_FRIEND_REQUEST = 'send_friend_request'         # Command to send a friend request arguments: pass the values as of 'client_id' eg: {'command': 'send_friend_request', 'data': {'client_id': '1'}}
ACCEPT_FRIEND_REQUEST = 'accept_friend_request'     # Command to accept a friend request arguments: pass the values as of 'client_id' eg: {'command': 'accept_friend_request', 'data': {'client_id': '1'}}
REJECT_FRIEND_REQUEST = 'reject_friend_request'     # Command to reject a friend request arguments: pass the values as of 'client_id' eg: {'command': 'reject_friend_request', 'data': {'client_id': '1'}}
CANCEL_FRIEND_REQUEST = 'cancel_friend_request'     # Command to cancel a friend request arguments: pass the values as of 'client_id' eg: {'command': 'cancel_friend_request', 'data': {'client_id': '1'}}
GET_USER_INFO = 'get_user_info'                     # Command to get user info arguments: pass the values as of 'client_id' eg: {'command': 'get_user_info', 'data': {'client_id': '35'}}
INVITE_TO_TOURNAMENT = 'invite_to_tournament'       # Command to invite a user to a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'invite_to_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
ACCEPT_TOURNAMENT = 'accept_tournament'             # Command to accept a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'accept_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
REJECT_TOURNAMENT = 'reject_tournament'             # Command to reject a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'reject_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
CANCEL_TOURNAMENT = 'cancel_tournament'             # Command to cancel a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'cancel_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
NEXT_MATCH = 'next_match'   