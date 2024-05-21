# constants.py

# Constants
LOBBY_NAME = 'lobby'                                # Name of the lobby

# Endpoints and commands (Client -> Server)
LIST_OF_USERS = 'list_of_users'                     # Command to send the list of online users (Connected to the socket)
LIST_SENT_INVITES = 'list_sent_invites'             # Command to send the list of invites sent
LIST_RECEIVED_INVITES = 'list_received_invites'     # Command to send the list of invites received
SEND_PRV_MSG = 'send_prv_msg'                       # Command to send a private message arguments: pass the values as of 'client_id' and 'message' eg: {'command': 'send_prv_msg', 'data': {'client_id': '1', 'message': 'Hello'}}
SEND_NOTIFICATION = 'send_notification'             # Command to send a group wide notification arguments: pass the values as of 'message' eg: {'command': 'send_notification', 'data': {'message': 'Hello'}}
CMD_NOT_FOUND = 'command_not_found'                 # Command to send when a command is not found
CLOSE_CONNECTION = 'close_connection'               # Command to close the connection
CREATE_USER = 'create_user'                         # Command to create a user arguments: pass the values as of 'user_data'
MODIFY_USER = 'modify_user'                         # Command to modify a user arguments: pass the values as of 'changes'
SERVER_TIME = 'server_time'                         # Command to send the server time
INVITE_TO_MATCH = 'invite_to_match'                 # Command to invite a user to a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'invite_to_match', 'data': {'client_id': '1', 'match_id': '1'}}
ACCEPT_MATCH = 'accept_match'                       # Command to accept a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'accept_match', 'data': {'client_id': '1', 'match_id': '1'}}
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
JOIN_QUEUE = 'join_queue'                           # Command to join the queue arguments: pass the values as of 'client_id' eg: {'command': 'join_queue', 'data': {'queue_name': 'global'}}
LEAVE_QUEUE = 'leave_queue'                         # Command to leave the queue arguments: pass the values as of 'client_id' eg: {'command': 'leave_queue', 'data': {'queue_name': 'tournament_26'}}
CREATE_3v3 = 'create_tournament'                    # Command to create a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'create_3v3', 'data': {"tournament_name": "cawabonga"}}
JOIN_3v3 = 'join_tournament'                        # Command to join a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'join_3v3'}
START_3v3 = 'start_tournament'                      # Command to start a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'start_3v3'}
NEXT_MATCH = 'next_match'   