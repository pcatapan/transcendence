import random
from django.utils import timezone
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async

class TournamentManager:
    def __init__(self):
        self.tournaments = {}

    async def create_tournament(self, user_id, tournament_name):
        if user_id in self.tournaments:
            await self.send_info_to_client('tournament_exists', user_id, {
                'message': 'You are already in a tournament'
            })
            return

        tournament_id = random.randint(1000, 9999)  # Generate a random tournament ID
        self.tournaments[user_id] = {
            'id': tournament_id,
            'name': tournament_name,
            'admin': user_id,
            'players': [user_id],
            'open': True
        }

        await self.send_info_to_client('tournament_created', user_id, {
            'tournament_name': tournament_name,
            'tournament_id': tournament_id
        })

    async def join_tournament(self, user_id):
        for tournament in self.tournaments.values():
            if tournament['open']:
                tournament['players'].append(user_id)
                tournament['open'] = False  # Close the tournament once a player joins
                await self.send_info_to_client('joined_tournament', user_id, {
                    'tournament_name': tournament['name'],
                    'tournament_id': tournament['id']
                })
                await self.send_info_to_client('tournament_ready', tournament['admin'], {
                    'opponent': user_id,
                    'tournament_id': tournament['id']
                })
                return
        await self.send_info_to_client('no_tournaments_available', user_id, {
            'message': 'No tournaments available'
        })

    async def start_tournament(self, user_id):
        if user_id not in self.tournaments:
            await self.send_info_to_client('no_tournament', user_id, {
                'message': 'You are not in a tournament'
            })
            return

        tournament = self.tournaments[user_id]
        if user_id != tournament['admin']:
            await self.send_info_to_client('not_admin', user_id, {
                'message': 'You are not the admin'
            })
            return

        players = tournament['players']
        if len(players) < 2:
            await self.send_info_to_client('not_enough_players', user_id, {
                'message': 'Not enough players'
            })
            return

        random.shuffle(players)
        matches = [(players[i], players[i + 1]) for i in range(0, len(players) - 1, 2)]
        await self.send_info_to_client('tournament_started', user_id, {
            'tournament_name': tournament['name'],
            'matches': matches
        })

        for player1, player2 in matches:
            await self.send_info_to_client('match_created', player1, {'opponent': player2})
            await self.send_info_to_client('match_created', player2, {'opponent': player1})

    async def send_info_to_client(self, command, user_id, data):
        # Implement the logic to send a message to a specific client
        pass
