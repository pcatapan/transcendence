from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from ..models import Tournament
from api.authuser.models.custom_user import CustomUser 

@method_decorator([login_required, require_POST], name='dispatch')
class TournamentCreateView(View):
	def post(self, request):
		if not request.body:
			return JsonResponse({'message': 'Empty payload'}, status=400)

		try:
			data = json.loads(request.body)
		except json.JSONDecodeError:
			return JsonResponse({'message': 'Invalid JSON'}, status=400)

		name = data.get('name')
		if not name:
			return JsonResponse({'message': "The 'name' field is required"}, status=422)

		type = data.get('type', '1v1')
		end_date = data.get('end_date', None)
		round_number = data.get('round', 0)
		players_ids = data.get('players', [request.user.id])
		observers_ids = data.get('observers', [])

		valid_players, player_errors = validate_users_existence(players_ids)
		if not valid_players:
			return player_errors

		valid_observers, observer_errors = validate_users_existence(observers_ids)
		if not valid_observers:
			return observer_errors

		tournament = Tournament(
			name=name,
			type=type,
			end_date=end_date,
			round=round_number,
			tournament_admin=request.user
		)

		try:
			tournament.save()
			tournament.players.set(valid_players)
			tournament.observers.set(valid_observers)
		except Exception as e:
			return JsonResponse({'message': str(e)}, status=400)

		response = JsonResponse({
			'status': 'ok',
			'tournament_id': tournament.id,
			'message': 'Tournament created successfully'
		})
		response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
		response['Access-Control-Allow-Headers'] = 'Content-Type'
		response['Access-Control-Allow-Origin'] = '*'

		return response

def validate_users_existence(user_ids):
	users = []
	errors = []

	for user_id in user_ids:
		try:
			user = CustomUser.objects.get(id=user_id)
			users.append(user)
		except CustomUser.DoesNotExist:
			errors.append(f"User with id {user_id} does not exist.")

	if errors:
		return False, JsonResponse({'status': 'error', 'message': errors}, status=404)
	
	return True, users
