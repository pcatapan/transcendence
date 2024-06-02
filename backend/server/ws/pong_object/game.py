import time
import random
import threading
import logging
from typing import Dict, Optional, Callable, Any, List, Tuple

from .player import Player
from .ball import Ball
from .paddle import Paddle
from .. import constants

logger = logging.getLogger(__name__)


class Game:

	_reaction_time = constants.AI_REACTION
	
	def __init__(
		self,
		dictKeyboard: Dict[str, bool],
		leftPlayer: Player,
		rightPlayer: Player,
		enclosure: Optional[Dict[str, int]] = None,
		scoreLimit: int = 10,
		ia_opponent: bool = False
	):
		try :
			self._leftPlayer = leftPlayer
			self._rightPlayer = rightPlayer
			self._scoreLimit = int(scoreLimit)
			self._dictKeyboard = dictKeyboard
			self._ia_opponent = ia_opponent

			self._dictPaddleCommands = {}
			self._dictCanvas = {}
			self._scoreReporter = {}

			self._enclosure = enclosure if enclosure else {"xl": 0, "xh": 850, "yl": 0, "yh": 520}

			self._ball = Ball(
				dictCanvas = self._dictCanvas, 
				name = "ball",
				position = {"x": 0,	"y":0},
				speed = {"x" : 0, "y" : 0},
				size = {"x" : 10, "y" : 10}
			)

			self._leftPaddle = Paddle(
				keyboard=self._dictKeyboard,
				dictCanvas = self._dictCanvas,
				name = "leftPaddle",
				position= {"x" : self._enclosure["xl"] + 30, "y" : self._enclosure["yl"]},
				speed = {"x" : 10, "y": 10}, 
				size = {"x":10, "y":100},
				binds = self._leftPlayer.binds,
				enclosure = self._enclosure
			)

			self._rightPaddle = Paddle(
				keyboard=self._dictKeyboard,
				dictCanvas = self._dictCanvas,
				name = "rightPaddle",
				position= {"x" : self._enclosure["xh"] - 30, "y" : self._enclosure["yl"]},
				speed = {"x" : 10, "y": 10}, 
				size = {"x":10, "y":100},
				binds = self._rightPlayer.binds,
				enclosure=self._enclosure
			)

			self._rightPlayer.reset_score()
			self._leftPlayer.reset_score()

			self._ball.addColider(self._leftPaddle)
			self._ball.addColider(self._rightPaddle)

			self.resetPosition()
			self.reportScore()

			self._frame = 0
			self._delayedActions: Dict[int, List[Tuple[Callable, Tuple[Any], Dict[str, Any]]]] = {}
			self._last_update_time = time.time()
		except Exception as e:
			logger.error(f"Error in Game.__init__: {e}")

	def reportScore(self):
		try :
			self._scoreReporter[self._leftPlayer.name] = self._leftPlayer.score
			self._scoreReporter[self._rightPlayer.name] = self._rightPlayer.score
			return self._scoreReporter.copy()
		except Exception as e:
			logger.error(f"Error in Game.reportScore: {e}")
	
	def resetPosition(self):
		try :
			# Calcola la posizione centrale dell'enclosure e imposta la posizione della palla
			center_x = (self._enclosure["xl"] + self._enclosure["xh"]) / 2
			center_y = (self._enclosure["yl"] + self._enclosure["yh"]) / 2
			self._ball.position = {"x": center_x, "y": center_y}

			# Genera un numero casuale tra 0 e 1 per determinare la nuova velocità della palla
			ran = random.uniform(0, 1)

			# Assegna una nuova velocità alla palla basata sul valore casuale generato
			if ran < 0.25:
				self._ball.speed = {"x": 2, "y": 1}
			elif ran < 0.5:
				self._ball.speed = {"x": -2, "y": 1}
			elif ran < 0.75:
				self._ball.speed = {"x": 2, "y": -1}
			else:
				self._ball.speed = {"x": -2, "y": -1}
		except Exception as e:
			logger.error(f"Error in Game.resetPosition: {e}")

	def pointLoop(self, run_delayed_actions: bool = True):
		if run_delayed_actions:
			self.runDelayedActions()

		self._ball.draw()
		ballState = self._ball.updatePosition()

		# la palla ha superato il bordo destro
		if ballState == 1:
			self._leftPlayer.goal()
			self.reportScore()
			self.resetPosition()
		# la palla ha superato il bordo sinistro
		elif ballState == -1:
			self._rightPlayer.goal()
			self.reportScore()
			self.resetPosition()
		# si gioca normalmente
		else:
			self._leftPaddle.draw()
			self._leftPaddle.updatePosition()

			if self._ia_opponent:
				self.update_ai_paddle()  # Aggiorna la posizione della paletta dell'IA
			else:
				self._rightPaddle.draw()
				self._rightPaddle.updatePosition()

		self._frame += 1

	def reportScreen(self):
		return self._dictCanvas.copy()		
	
	def addDelayedAction(self, frame, function, *args, **kwargs):
		if frame not in self._delayedActions:
			self._delayedActions[frame] = []
		self._delayedActions[frame].append((function,args,kwargs))

	def runDelayedActions(self) -> None:
		actions = self._delayedActions.pop(self._frame, [])

		for fun, args, kwargs in actions:
			try:
				fun(*args, **kwargs)
			except Exception as e:
				logger.error(f"Error in runDelayedActions: {e}")

	def update_ai_paddle(self):
		try:
			# Logica per seguire la palla con tempi di reazione
			current_time = time.time()
			if current_time - self._last_update_time < self._reaction_time:
				return  # Aspetta fino al prossimo aggiornamento

			ball_pos = self._ball.position
			paddle_pos = self._rightPaddle.position
			paddle_size = self._rightPaddle.size

			# Previsione della posizione futura della palla
			predicted_y = ball_pos["y"] + self._ball.speed["y"] * self._reaction_time * constants.BASE_FPS

			if predicted_y > paddle_pos["y"] + paddle_size["y"] // 2:
				self._rightPaddle.speed = {"x": 0, "y": 10}
			elif predicted_y < paddle_pos["y"] - paddle_size["y"] // 2:
				self._rightPaddle.speed = {"x": 0, "y": -10}
			else:
				self._rightPaddle.speed = {"x": 0, "y": 0}

			self._rightPaddle.updatePosition()
			self._last_update_time = current_time

		except Exception as e:
			logger.error(f"Error in update_ai_paddle: {e}")


