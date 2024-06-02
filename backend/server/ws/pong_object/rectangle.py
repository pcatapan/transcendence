from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MovingRectangle(ABC):
    
    def __init__(self):
        pass

    def initialize(self,
        dictCanvas: Dict[str, Dict[str, int]],
        name: str, 
        position: Optional[Dict[str, int]] = None, 
        speed: Optional[Dict[str, int]] = None, 
        size: Optional[Dict[str, int]] = None, 
        enclosure: Optional[Dict[str, int]] = None
    ):
        try :
            self._position = position if position else {"x": 0, "y": 0}
            self._speed = speed if speed else {"x": 0, "y": 0}
            self._size = size if size else {"x": 0, "y": 0}
            self._enclosure = enclosure if enclosure else {"xl": 0, "xh": 858, "yl": 0, "yh": 525}
            
            self._dictCanvas = dictCanvas
            self._name = name
            self._dictCanvas[name] = {}
            
            self.updateCorners()
        except Exception as e:
            logger.error(f"Error in MovingRectangle.initialize: {e}")

    @property
    def position(self) -> Dict[str, int]:
        return self._position
    
    @position.setter
    def position(self, value: Dict[str, int]) -> None:
        self._position = value
        self.updateCorners()
    
    @property
    def speed(self) -> Dict[str, int]:
        return self._speed
    
    @speed.setter
    def speed(self, value: Dict[str, int]) -> None:
        self._speed = value

    @property
    def size(self) -> Dict[str, int]:
        return self._size
    
    @size.setter
    def size(self, value: Dict[str, int]) -> None:
        self._size = value
        self.updateCorners()

    @property
    def color(self) -> str:
        return self._color
    
    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @property
    def corners(self) -> Dict[str, int]:
        return self._corners
    
    @property
    def enclosure(self) -> Dict[str, int]:
        return self._enclosure

    def updateCorners(self) -> None:
        self._corners = {
            "xl": self._position["x"],
            "xh": self._position["x"] + self._size["x"],
            "yl": self._position["y"],
            "yh": self._position["y"] + self._size["y"]
        }

    def draw(self) -> None:
        self._dictCanvas[self._name]["position"] = self.position
        self._dictCanvas[self._name]["size"] = self.size
        self._dictCanvas[self._name]["speed"] = self.speed

    @abstractmethod
    def updatePosition(self) -> None:
        pass
