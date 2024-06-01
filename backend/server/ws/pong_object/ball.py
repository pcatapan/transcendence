from typing import Dict, Optional
import logging

from .rectangle import MovingRectangle

logger = logging.getLogger(__name__)

class Ball(MovingRectangle):
	
	# enclousure avrà valori che non sono nel altezza e larghezza del canvas 
	def __init__(self,
		dictCanvas: dict,
		name: str,
		position: Optional[Dict[str, int]] = None,
		speed: Optional[Dict[str, int]] = None,
		size: Optional[Dict[str, int]] = None,
		enclousure: Optional[Dict[str, int]] = None
	) -> None:
		
		if position is None:
			position = {"x": 0, "y": 0}
		if speed is None:
			speed = {"x": 0, "y": 0}
		if size is None:
			size = {"x": 10, "y": 10}
			
		self.initialize(
			dictCanvas = dictCanvas,
			name = name,
			position = position,
			speed = speed, 
			size = size,
			enclousure = enclousure
		)

		self._collide = []
		self.speed_multiplier = 1.0	

	def checkCollision(self, colider: MovingRectangle) -> bool:

		corners = self.corners
		colider_corners = colider.corners

		# Controllo se ci sono collisioni tra i due oggetti
		return (
			(colider_corners["xl"] <= corners["xl"] <= colider_corners["xh"] and
			 colider_corners["yl"] <= corners["yl"] <= colider_corners["yh"]) or
			(colider_corners["xl"] <= corners["xh"] <= colider_corners["xh"] and
			 colider_corners["yl"] <= corners["yl"] <= colider_corners["yh"]) or
			(colider_corners["xl"] <= corners["xl"] <= colider_corners["xh"] and
			 colider_corners["yl"] <= corners["yh"] <= colider_corners["yh"]) or
			(colider_corners["xl"] <= corners["xh"] <= colider_corners["xh"] and
			 colider_corners["yl"] <= corners["yh"] <= colider_corners["yh"])
		)
	
	def collisionHandler(self, colider: MovingRectangle):
		corners = self.corners
		colider_corners = colider.corners

		# Calcolo l'intersezione tra i due oggetti
		leftInter = max(corners["xl"], colider_corners["xl"])
		rightInter = min(corners["xh"], colider_corners["xh"])

		# Calcolo la proporzione del movimento che si sovrappone
		adj = abs(leftInter - rightInter) / abs(self.speed["x"])

		# Annulla il movimento della palla per rimuovere la sovrapposizione
		self.position = dict(
			x=self.position["x"] - adj * self.speed["x"],
			y=self.position["y"] - adj * self.speed["y"]
		)
	
		# Calcolo la direzione della collisione
		# determinando quale lato del rettangolo è stato colpito
		x1 = abs(corners["xl"] - colider_corners["xh"])
		x2 = abs(corners["xh"] - colider_corners["xl"])
		y1 = abs(corners["yl"] - colider_corners["yh"])
		y2 = abs(corners["yh"] - colider_corners["yl"])
	
		# In base al lato colpito, inverto la direzione della palla
		if min(x2, x1) < min(y1, y2):
			self.speed = dict(
				x=-self.speed["x"], 
				y=self.speed["y"] + 0.5 * colider.speed["y"]
			)
		else:
			self.speed = dict(
				x=self.speed["x"] + 0.5 * colider.speed["x"],
				y=-self.speed["y"]
			)

	def updatePosition(self) -> int:
		# Controlla se la palla ha superato il bordo destro dell'enclosure
		if self.position["x"] + self.size["x"] >= self.enclousure["xh"]:
			# Inverte la direzione della palla
			self.speed = {
				"x": -self.speed["x"],
				"y": self.speed["y"]
			}
			return 1
		
		# Controlla se la palla ha superato il bordo sinistro dell'enclosure
		if self.position["x"] < self.enclousure["xl"]:
			# Inverte la direzione della palla
			self.speed = {
				"x": -self.speed["x"],
				"y": self.speed["y"]
			}
			return -1
	
		# Controlla se la palla ha superato il bordo superiore o inferiore dell'enclosure
		if self.position["y"] + self.size["y"] > self.enclousure["yh"] \
			or self.position["y"] < self.enclousure["yl"]\
		:
			# Inverte la direzione della palla
			self.speed = {
				"x": self.speed["x"],
				"y": -self.speed["y"]
			}
		
		# Controlla se la palla ha colliso con un oggetto
		for ele in self._collide:
			if self.checkCollision(ele):
				self.collisionHandler(ele)
		
		# Aggiorna la posizione della palla
		self.position = {
			"x": self.position["x"] + self.speed["x"] * self.speed_multiplier,
			"y": self.position["y"] + self.speed["y"] * self.speed_multiplier
		}
		return 0
	
	def addColider(self, colider: MovingRectangle):
		self._collide.append(colider)
