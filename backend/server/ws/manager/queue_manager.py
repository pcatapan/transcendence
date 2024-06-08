from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from channels.db import database_sync_to_async
from .. import constants

import logging

logger = logging.getLogger(__name__)

elo_diff = constants.ELO_DIFF

class QueueManager():

	def __init__(self):
		self.queues = {}
		self.pending_matches = {}

	async def join_queue(self, queue_name, consumer):
		if queue_name not in self.queues:
			self.queues[queue_name] = []

		# TODO: controllare se l'utente ha una partita pendente
		
		if not any(user['id'] == consumer.user.id for user in self.queues[queue_name]):
			self.queues[queue_name].append({
				'id': consumer.user.id,
				'elo': consumer.user.ELO
			})
			self.queues[queue_name].sort(key=lambda x: x['elo'])

			await consumer.send_layer(queue_name, command=constants.JOIN_QUEUE)

			await self.find_opponent(queue_name, consumer)

		else:
			consumer.send_layer('Already in the queue', command=constants.JOIN_QUEUE, status='400')

	async def leave_queue(self, queue_name, consumer):
		if queue_name in self.queues:
			self.queues[queue_name] = [user for user in self.queues[queue_name] if user['id'] != consumer.user.id]

			await consumer.send_layer(queue_name, command=constants.LEAVE_QUEUE)
		else:
			await consumer.send_layer('Queue not found', command=constants.LEAVE_QUEUE, status='404')

	async def find_opponent(self, queue_name, consumer):
		logger.info(f"Finding opponent for {consumer.user.username}")
		logger.info(f"Queue: {self.queues[queue_name]}")
		if len(self.queues[queue_name]) < 2:
			await consumer.send_layer(
				'Not enough players in the queue, waiting for more players',
				command=constants.JOIN_QUEUE,
				status='200'
			)
			return

		# Trova l'indice dell'utente nella coda
		user_id = consumer.user.id
		user_index = next(i for i, user in enumerate(self.queues[queue_name]) if user['id'] == user_id)

		# Cerca l'avversario con ELO più vicino e con una differenza di ELO inferiore a elo_diff
		opponent_index = None
		for i in range(len(self.queues[queue_name])):
			if i != user_index and abs(self.queues[queue_name][i]['elo'] - consumer.user.ELO) < elo_diff:
				opponent_index = i
				break
		
		if opponent_index is None:
			await consumer.send_layer(
				'No opponent found, waiting for more players',
				command=constants.JOIN_QUEUE,
				status='200'
			)
			return

		opponent = self.queues[queue_name][opponent_index]

		match_id = await self.create_match(consumer.user, opponent['id'])
		if match_id is None:
			await consumer.send_layer(
				'Error creating match',
				command=constants.JOIN_QUEUE,
				status='400'
			)
			return

		opponent_channel_name = consumer.user_manager.get_user_channel(str(opponent['id']))
		user_channel_name = consumer.user_manager.get_user_channel(str(user_id))

		message_user = {
			'match_id': match_id,
			'palyer_1': user_id,
			'player_2': opponent['id'],
			'opponent': consumer.user_manager.get_user(str(opponent['id'])),
		}

		message_opponent = {
			'match_id': match_id,
			'palyer_1': user_id,
			'player_2': opponent['id'],
			'opponent': consumer.user_manager.get_user(str(user_id)),
		}

		await consumer.channel_layer.send(user_channel_name, {
			'status': 200,
			'type': "unicast",
			'command': constants.FOUND_OPPONENT,
			'next_command': 'confirm_match',
			'content': message_user,
			'meta': {
				"channel": "lobby",
				"priority": 'normal',
			}
		})

		await consumer.channel_layer.send(opponent_channel_name, {
			'status': 200,
			'type': "unicast",
			'command': constants.FOUND_OPPONENT,
			'next_command': 'confirm_match',
			'content': message_opponent,
			'meta': {
				"channel": "lobby",
				"priority": 'normal',
			}
		})

		

		try:
			self.queues[queue_name].remove({'id': user_id, 'elo': consumer.user.ELO})
			self.queues[queue_name].remove(opponent)
		except ValueError as e:
			logger.error(f"Error removing users from queue: {e}")

	@database_sync_to_async
	def create_match(self, user, opponent_id):
		try:
			Match = import_string('api.tournament.models.Match')
			User = import_string('api.authuser.models.CustomUser')

			opponent = get_object_or_404(User, pk=opponent_id)

			match = Match.objects.create(
				player1=user,
				player2=opponent,
				active=False
			)

			match.save()

			self.pending_matches[match.id] = {
				'player1': user.id,
				'player1_obj' : user,
				'player1_confirmed': False,
				'player2': opponent.id,
				'player2_obj' : opponent,
				'player2_confirmed': False,
				'match_id': match.id,
			}

			return match.id
		
		except Exception as e:
			logger.error(f"Error creating match: {e}")
			return None

	#Uso la funzione per confermare che enrambi i client abbiano ricevuto i dettagli del match
	# e che siano pronti a iniziare
	async def confirm_match(self, match_id, consumer):
		if match_id in self.pending_matches:
			match = self.pending_matches[match_id]

			if match['player1'] == consumer.user.id:
				match['player1_confirmed'] = True
			elif match['player2'] == consumer.user.id:
				match['player2_confirmed'] = True

			if match.get('player1_confirmed') and match.get('player2_confirmed'):
				player_1_channel_name = consumer.user_manager.get_user_channel(str(match['player1']))
				player_2_channel_name = consumer.user_manager.get_user_channel(str(match['player2']))

				match_url = 'ws/pong/' + str(match_id)

				await consumer.channel_layer.send(player_1_channel_name, {
					'status': 200,
					'type': "unicast",
					'command': constants.START_BALL,
					'content': match_url,
					'meta': {
						"channel": "lobby",
						"priority": 'normal',
					}
				})

				await consumer.channel_layer.send(player_2_channel_name, {
					'status': 200,
					'type': "unicast",
					'command': constants.START_BALL,
					'content': match_url,
					'meta': {
						"channel": "lobby",
						"priority": 'normal',
					}
				})
		else:
			await consumer.send_layer(
				'Match not found',
				command=constants.CONFIRM_MATCH,
				status='404'
			)

