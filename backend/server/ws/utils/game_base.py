import logging
import asyncio
import time
from .. import constants

logger = logging.getLogger(__name__)

class GameBase :
	def set_frame_rate(self, fps):
		if fps < 1 or fps > 60 or not isinstance(fps, int):
			fps = constants.BASE_FPS
		return 1 / fps
	
	async def check_reconnect(self, len = 2):
		try:
			for seconds in range(constants.SECOND_WAIT):
				try:
					await self.broadcast_layer(
						{
							"message": "Waiting for opponent to reconnect",
							"seconds_left": f"{constants.SECOND_WAIT - seconds - 1} seconds"
						},
						str(self.match_id),
						constants.WAITING_FOR_OPPONENT,
					)
					await asyncio.sleep(1)
				except Exception as e:
					logger.error(f"Error during check_reconnect - broadcast_layer: {e}")
					return

				try :
					if len(self.match_manager.list_of_players[self.match_id]) == len:
						logger.info(f"Both players reconnected in match {self.match_id}. Resuming game.")
						self.run_game[self.match_id] = True
						self.shared_game_task[self.match_id] = asyncio.create_task(self.async_proces_game(None))
						return
				except Exception as e:
					logger.error(f"Error during check_reconnect - list_of_players: {e}")
					return

			# If the loop completes without both players reconnecting, close the match
			logger.info(f"Opponent did not reconnect within the time limit for match {self.match_id}. Closing match.")
			await self.close()

		except Exception as e:
			logger.error(f"Error during check_reconnect: {e}")
			await self.close()
	
	async def async_proces_game(self, data):
		try:
			frame_rate = self.set_frame_rate(constants.BASE_FPS)
			match_id = self.match_id
			game = self.shared_game[match_id]
			start_time = time.time()

			prev_state = None

			while self.run_game[match_id]:
				game.pointLoop()

				left_score = game._leftPlayer.score
				right_score = game._rightPlayer.score
				elapsed_time = time.time() - start_time

				current_state = {
					"canvas": game.reportScreen(),
					"left_score": left_score,
					"right_score": right_score,
					"elapsed_time": elapsed_time
				}

				if left_score >= self.scorelimit or right_score >= self.scorelimit:
					self.run_game[match_id] = False
					await self.broadcast_layer(
						current_state,
						str(match_id),
						constants.UPDATE_GAME,
					)

					await self.broadcast_layer(
						await self.save_models(),
						str(match_id),
						constants.FINISH_MATCH,
						priority='high',
					)
					self.finished[match_id] = True

					await asyncio.sleep(0.5)
					await self.close_with_timeout()
					return
				
				if prev_state != current_state:
					await self.broadcast_layer(
						current_state,
						str(match_id),
						constants.UPDATE_GAME,
					)
					await asyncio.sleep(frame_rate)
					prev_state = current_state

			await asyncio.sleep(1)

			if self.finished[match_id]:
				await self.close_with_timeout()

		except asyncio.CancelledError:
			logger.info('Game stopped')
		except Exception as e:
			logger.error(f"Error during aync_proces_game: {e}")
			await self.close_with_timeout()

	async def close_with_timeout(self, code=1000):
		try:
			await asyncio.wait_for(self.close(code), timeout=5)
		except asyncio.TimeoutError:
			logger.warning("Closing the WebSocket took too long and was forcefully terminated.")

	async def discard_channels(self):
		try:
			await self.channel_layer.group_discard(
				f"{self.match_id}",
				self.channel_name
			)
			await self.channel_layer.group_discard(
				f"{self.match_id}.player.{self.player_1_id}",
				self.channel_name
			)
			await self.channel_layer.group_discard(
				f"{self.match_id}.player.{self.player_2_id}",
				self.channel_name
			)
		except Exception as e:
			logger.error(f"Error during discard_channels: {e}")
			await self.close()

