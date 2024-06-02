from typing import Dict, Optional
from .rectangle import MovingRectangle
import logging

logger = logging.getLogger(__name__)

class Paddle(MovingRectangle):
	
	def __init__(
		self, 
		dictCanvas: Dict[str, Dict[str, int]], 
		name: str, 
		keyboard: Dict[str, bool],
		position: Optional[Dict[str, int]] = None,
		speed: Optional[Dict[str, int]] = None,
		size: Optional[Dict[str, int]] = None,
		binds: Optional[Dict[str, str]] = None,
		enclosure: Optional[Dict[str, int]] = None
	) -> None:
		try:
			# Inizializza i valori di default
			if position is None:
				position = {"x": 30, "y": 0}
			if speed is None:
				speed = {"x": 10, "y": 10}
			if size is None:
				size = {"x": 10, "y": 30}
			if binds is None:
				binds = {
					"up": "UNUSED_DEFAULT_KEY", 
					"down": "UNUSED_DEFAULT_KEY",
					"left": "UNUSED_DEFAULT_KEY", 
					"right": "UNUSED_DEFAULT_KEY"
				}
			
			# Inizializza la classe base MovingRectangle
			self.initialize(
				dictCanvas=dictCanvas, 
				name=name, 
				position=position, 
				speed=speed, 
				size=size, 
				enclosure=enclosure
			)
			
			self._binds = binds
			self._maxSpeed = speed
			self._keyboard = keyboard
			
			# Inizializza lo stato dei tasti a False
			for value in binds.values():
				self._keyboard[value] = False
		except Exception as e:
			logger.error(f"Error in Paddle.__init__: {e}")

	@property
	def maxSpeed(self) -> Dict[str, int]:
		return self._maxSpeed
	
	def updatePosition(self) -> None:

		# Calcola la velocità lungo l'asse x basata sull'input della tastiera
		xSpeed = (self._keyboard[self._binds["right"]] - 
				  self._keyboard[self._binds["left"]]) * self.maxSpeed["x"]
		# Calcola la velocità lungo l'asse y basata sull'input della tastiera
		ySpeed = (self._keyboard[self._binds["down"]] - 
				  self._keyboard[self._binds["up"]]) * self.maxSpeed["y"]
		
		# Verifica se xSpeed e ySpeed sono valori numerici
		xSpeed = 0 if not isinstance(xSpeed, (int, float)) else xSpeed
		ySpeed = 0 if not isinstance(ySpeed, (int, float)) else ySpeed
		
		# Impedisce al paddle di muoversi fuori dall'area di gioco lungo l'asse x
		if xSpeed < 0 and self.position["x"] <= self.enclosure["xl"]:
			xSpeed = 0
		if xSpeed > 0 and self.position["x"] + self.size["x"] >= self.enclosure["xh"]:
			xSpeed = 0
		
		# Impedisce al paddle di muoversi fuori dall'area di gioco lungo l'asse y
		if ySpeed < 0 and self.position["y"] <= self.enclosure["yl"]:
			ySpeed = 0
		if ySpeed > 0 and self.position["y"] + self.size["y"] >= self.enclosure["yh"]:
			ySpeed = 0
		
		# Calcola la nuova posizione del paddle
		xNewPos = self.position["x"] + xSpeed
		yNewPos = self.position["y"] + ySpeed
		
		# Limita la nuova posizione all'interno dell'area di gioco
		xNewPos = max(self.enclosure["xl"], min(xNewPos, self.enclosure["xh"] - self.size["x"]))
		yNewPos = max(self.enclosure["yl"], min(yNewPos, self.enclosure["yh"] - self.size["y"]))
		
		# Aggiorna la posizione e la velocità del paddle
		self.position = {"x": xNewPos, "y": yNewPos}
		self.speed = {"x": xSpeed, "y": ySpeed}