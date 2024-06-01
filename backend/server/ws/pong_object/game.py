import time
import random
import threading
import logging
from typing import Dict, Optional, Callable, Any, List, Tuple

from .player import Player
from .ball import Ball
from .paddle import Paddle

logger = logging.getLogger(__name__)

class Game:
	def __init__(
		self,
		dictKeyboard: Dict[str, bool],
		leftPlayer: Player,
		rightPlayer: Player,
		enclousure: Optional[Dict[str, int]] = None,
		scoreLimit: int = 10
	):
		self._leftPlayer = leftPlayer
		self._rightPlayer = rightPlayer
		self._scoreLimit = int(scoreLimit)
		self._dictKeyboard = dictKeyboard

		self._dictPaddleCommands = {}
		self._dictCanvas = {}
		self._scoreReporter = {}

		self._enclousure = enclousure if enclousure else {"xl": 0, "xh": 858, "yl": 0, "yh": 525}

		self._ball = Ball(
			dictCanvas = self._dictCanvas, 
			name ="ball",
			position = {"x": 0,	"y":0},
			speed = {"x" : 0, "y" : 0},
			size = {"x" : 10, "y" : 10}
		)

		self._leftPaddle = Paddle(
			keyboard=self._dictKeyboard,
			dictCanvas = self._dictCanvas,
			name = "leftPaddle",
			position= {"x" : self._enclousure["xl"] + 30, "y" : self._enclousure["yl"]},
			speed = {"x" : 10, "y": 10}, 
			size = {"x":10, "y":100},
			binds = self._leftPlayer.binds(),
			enclousur = self._enclousure
		)

		self._rightPaddle = Paddle(
			keyboard=self._dictKeyboard,
			dictCanvas = self._dictCanvas,
			name = "rightPaddle",
			position= {"x" : self._enclousure["xh"] - 30, "y" : self._enclousure["yl"]},
			speed = {"x" : 10, "y": 10}, 
			size = {"x":10, "y":100},
			binds = self._rightPlayer.binds(),
			enclousure=self._enclousure
		)

		self._rightPlayer.reset_score()
		self._leftPlayer.reset_score()

		self._ball.addColider(self._leftPaddle)
		self._ball.addColider(self._rightPaddle)

		self.resetPosition()
		self.reportScore()

		self._frame = 0
		self._delayedActions: Dict[int, List[Tuple[Callable, Tuple[Any], Dict[str, Any]]]] = {}

	def reportScore(self):
		self._scoreReporter[self._leftPlayer.name] = self._leftPlayer.score
		self._scoreReporter[self._rightPlayer.name] = self._rightPlayer.score
		return self._scoreReporter.copy()
	
	def resetPosition(self):
		# Calcola la posizione centrale dell'enclosure e imposta la posizione della palla
		center_x = (self._enclousure["xl"] + self._enclousure["xh"]) / 2
		center_y = (self._enclousure["yl"] + self._enclousure["yh"]) / 2
		self._ball.position = {"x": center_x, "y": center_y}

		# Genera un numero casuale tra 0 e 1 per determinare la nuova velocità della palla
		ran = random.uniform(0, 1)

		# Assegna una nuova velocità alla palla basata sul valore casuale generato
		if ran < 0.25:
			self._ball.speed = {"x": 4, "y": 1}
		elif ran < 0.5:
			self._ball.speed = {"x": -4, "y": 1}
		elif ran < 0.75:
			self._ball.speed = {"x": 4, "y": -1}
		else:
			self._ball.speed = {"x": -4, "y": -1}

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

