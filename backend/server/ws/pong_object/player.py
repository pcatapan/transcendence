from typing import Dict

class Player:
	def __init__(self, name: str = "Player", binds: Dict[str, str] = None):
		if binds is None:
			binds = {
				"up": "UNUSED_DEFAULT_KEY",
				"down": "UNUSED_DEFAULT_KEY",
				"left": "UNUSED_DEFAULT_KEY", 
				"right": "UNUSED_DEFAULT_KEY"
			}
		self._name = name
		self._binds = binds
		self._score = 0

	@property
	def score(self) -> int:
		return self._score
	
	@property
	def name(self) -> str:
		return self._name
	
	@property
	def binds(self) -> Dict[str, str]:
		return self._binds
	
	def goal(self) -> None:
		self._score += 1

	def reset_score(self) -> None:
		self._score = 0
