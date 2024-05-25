import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ..pong.game import Game
from ..pong.player import Player
from ..manager.match_manager import MatchManager
from channels.db import database_sync_to_async
from django.utils.module_loading import import_string
from django.utils import timezone
from django.db import transaction
from ..utils.message import Message

from .. import constants
import logging

logger = logging.getLogger(__name__)

User = import_string('api.authuser.models.CustomUser')

def set_frame_rate(fps):
    if fps < 1 or fps > 60 or not isinstance(fps, int):
        fps = 60
    return 1 / fps

class Pong(AsyncWebsocketConsumer, Message):
    match_manager = MatchManager()

    shared_game_keyboard = {}
    shared_game_task = {}
    shared_game = {}
    run_game = {}
    finished = {}
    scorelimit = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_object = None
        self.keyboard = {}
        self.left_player = None
        self.right_player = None
        self.player_1_id = None
        self.player_2_id = None
        self.player_1_score = 0
        self.player_2_score = 0
        self.match_object = None
        self.match_id = None
        self.client_id = None

    async def connect(self):
        try:

            user = self.scope['user']
            if user.is_authenticated:
                self.player_object = user
            else:
                await self.close(code=4001)
            
            self.client_id = str(user.id)
            match_id = self.scope['url_route']['kwargs']['match_id']
            self.room_group_name = f'match_{match_id}'

            self.match_object = await self.match_manager.get_match_and_player(match_id)
            if not self.match_object or user.id in {self.match_object.player1.id, self.match_object.player2.id}:
                await self.close()

            if not self.match_object.active:
                await self.send_layer(
                    content="Match is not active",
                    status=400,
                    channel=constants.GAME_NAME
                )
                await self.close()

            await self.channel_layer.group_add(f"{self.match_id}.client_id", self.channel_name)
            await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
            
            await self.load_models(self.match_id)
                
            await self.accept()

            Pong.finished[self.match_id] = False
                        
            await self.broadcast_layer(
                content={
                    "message": "User Connected",
                    "connected_users": self.match_manager.get_list_of_players_rtr(self.match_id)
                },
                channel=f"{self.match_id}"
            )
            
            if self.match_manager.player_in_list(self.player_1_id, self.match_id) and \
            self.match_manager.player_in_list(self.player_2_id, self.match_id):
                await self.broadcast_layer(
                    content="Game Ready",
                    channel=f"{self.match_id}"
                )
            else:
                await self.broadcast_layer(
                    content="Waiting for opponent, please wait",
                    channel=f"{self.match_id}"
                )
                  
        except Exception as e:
            await self.close()
            logger.error(f"Error during connect: {e}")

    async def disconnect(self, close_code=1000):
        if self.client_id in Pong.list_of_players[self.match_id]:
            del Pong.list_of_players[self.match_id][self.client_id]

        Pong.run_game[self.match_id] = False
        try:
            res = await self.save_models(disconnect=True)
            if res:
                await self.broadcast_to_group(str(self.match_id), "match_finished", res)
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

        await self.discard_channels()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if not data.get('command'):
                return

            if data['command'] == 'keyboard' and Pong.run_game[self.match_id]:
                await self.keyboard_input(data)
            elif data['command'] == 'start_ball':
                Pong.run_game[self.match_id] = True
                Pong.shared_game_task[self.match_id] = asyncio.create_task(self.start_game(data))

        except Exception as e:
            logger.error(f"Error during receive: {e}")
            await self.close()


    @database_sync_to_async
    def load_models(self, match_id):
        try:

            self.player_1_id = str(self.match_object.player1.id)
            self.player_2_id = str(self.match_object.player2.id)

            # Inizializza o aggiorna la lista dei giocatori per il match corrente
            self.match_manager.inzialize_list_of_players(match_id, self.client_id, self)

            # Carica gli oggetti User per entrambi i giocatori
            self.match_manager.add_player(self.match_object.player1)
            self.match_manager.add_player(self.match_object.player2)

            # Configura i binding della tastiera per entrambi i giocatori
            self.keyboard = {
                self.player_1_id: self.match_manager.get_defoult_keyboard(self.player_1_id),
                self.player_2_id: self.match_manager.get_defoult_keyboard(self.player_2_id),
            }

            self.left_player = Player(
                name = self.player_1_id,
                binds = self.keyboard[self.player_1_id]
            )
            self.right_player = Player(
                name = self.player_2_id,
                binds = self.keyboard[self.player_2_id]
            )

            # Inizializza la tastiera condivisa del gioco
            Pong.shared_game_keyboard[self.match_id] = {
                f'up.{self.player_1_id}': False,
                f'down.{self.player_1_id}': False,
                f'up.{self.player_2_id}': False,
                f'down.{self.player_2_id}': False,
            }

            Pong.run_game[self.match_id] = False

            # Crea l'oggetto Game condiviso
            Pong.shared_game[self.match_id] = Game(
                dictKeyboard = Pong.shared_game_keyboard[self.match_id],
                leftPlayer = self.left_player,
                rightPlayer = self.right_player,
                scoreLimit = self.scorelimit,
            )

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.close()
    
    @database_sync_to_async
    @transaction.atomic
    def save_models(self, disconnect=False, close_code=1000):
        Match = import_string('api.tournament.models.match')
        User = import_string('api.authuser.models.CustomUser')

        if Pong.finished.get(self.match_id):
            return

        match_object = Match.objects.select_for_update().get(id=self.match_id)
        match_object.player1_score = Pong.shared_game[self.match_id]._leftPlayer.getScore()
        match_object.player2_score = Pong.shared_game[self.match_id]._rightPlayer.getScore()

        player1_id = self.player_1_id
        player2_id = self.player_2_id

        if disconnect:
            winner_id = player2_id if int(self.client_id) == int(player1_id) else player1_id
            match_object.winner = User.objects.get(id=winner_id)
        elif match_object.player1_score == match_object.player2_score:
            player1_elo = User.objects.get(id=player1_id).ELO
            player2_elo = User.objects.get(id=player2_id).ELO

            if player1_elo > player2_elo:
                match_object.winner = User.objects.get(id=player1_id)
            elif player1_elo < player2_elo:
                match_object.winner = User.objects.get(id=player2_id)
            else:
                match_object.winner = None
        else:
            match_object.winner = User.objects.get(id=player1_id if match_object.player1_score > match_object.player2_score else player2_id)

        match_object.date_played = timezone.now()
        match_object.active = False
        match_object.save()

        Pong.finished[self.match_id] = True

        if match_object.winner:
            winner_id = match_object.winner.id
            loser_id = match_object.loser().id

            winner_object = User.objects.get(id=winner_id)
            loser_object = User.objects.get(id=loser_id)

            elo_change = 15
            elo_change_per_player = elo_change / 2

            winner_object.ELO = max(0, winner_object.ELO + elo_change_per_player)
            loser_object.ELO = max(0, loser_object.ELO - elo_change_per_player)

            winner_object.save()
            loser_object.save()
            
            return {
                "winner_id": winner_id,
                "winner_username": match_object.winner.username if match_object.winner else None,
                "player1_id": match_object.player1.id,
                "player1_username": match_object.player1.username,
                "player2_id": match_object.player2.id,
                "player2_username": match_object.player2.username,
                "loser_id": loser_id,
                "player1_score": match_object.player1_score,
                "player2_score": match_object.player2_score,
                "winner_elo": winner_object.ELO,
                "loser_elo": loser_object.ELO,
            }
    
    async def check_reconnect(self):
        seconds_to_wait = 6
        for seconds in range(seconds_to_wait):
            await self.broadcast_to_group(self.match_id, "message", {
                "message": "Waiting for opponent to reconnect",
                "seconds_left": f"{seconds_to_wait - seconds - 1} seconds"
            })
            await asyncio.sleep(1)
            if len(Pong.list_of_players[self.match_id].keys()) == 2:
                Pong.run_game[self.match_id] = True
                Pong.shared_game_task[self.match_id] = asyncio.create_task(self.start_game())
                return


    async def keyboard_input(self, data):
        try:
            key_status = data.get('key_status')
            key = data.get('key')
            formatted_key = f'{key}.{self.client_id}'
            
            await asyncio.sleep(0.01)

            if key_status == 'on_press':
                Pong.shared_game_keyboard[self.match_id][formatted_key] = True
            elif key_status == 'on_release':
                Pong.shared_game_keyboard[self.match_id][formatted_key] = False
            else:
                logger.error(f'Unknown key status: {key_status}, {formatted_key}')
                    
        except Exception as e:
            logger.error(f"Error during keyboard_input: {e}")
            await self.close()
            
    async def start_game(self, data):
        try:
            while Pong.run_game[self.match_id]:
                Pong.shared_game[self.match_id].pointLoop2()

                left_score = Pong.shared_game[self.match_id]._leftPlayer.getScore()
                right_score = Pong.shared_game[self.match_id]._rightPlayer.getScore()

                if left_score >= self.scorelimit or right_score >= self.scorelimit:
                    Pong.run_game[self.match_id] = False
                    await self.broadcast_to_group(str(self.match_id), "match_finished", await self.save_models())
                    Pong.finished[self.match_id] = True
                    await asyncio.sleep(0.5)
                    await self.close()
                    return

                await self.broadcast_to_group(f"{self.match_id}", "screen_report", {
                    "game_update": Pong.shared_game[self.match_id].reportScreen(),
                    "left_score": left_score,
                    "right_score": right_score
                })
                await asyncio.sleep(set_frame_rate(60))

            await asyncio.sleep(0.5)
            if Pong.finished[self.match_id]:
                await self.close()
        except asyncio.CancelledError:
            logger.info('Game stopped')
        except Exception as e:
            logger.error(f"Error during start_game: {e}")
            await self.close()

    async def discard_channels(self):
        try:
            await self.channel_layer.group_discard(
                f"{self.match_id}",
                self.channel_name
            )
            await self.channel_layer.group_discard(
                f"{self.match_id}.player_1_id",
                self.channel_name
            )
            await self.channel_layer.group_discard(
                f"{self.match_id}.player_2_id",
                self.channel_name
            )
            
        except Exception as e:
            logger.error(f"Error during discard_channels: {e}")
            await self.close()
