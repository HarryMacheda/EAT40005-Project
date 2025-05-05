from abc import ABC, abstractmethod
from typing import Callable 

# Socket abstract class
class ASocket(ABC):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self._handler: Callable[[object], None] = print

    @abstractmethod
    def SendMessage(self, object: object):
        pass

    def AttachHandler(self, handler: Callable[[object], None]):
        self._handler = handler

    @abstractmethod
    def RunListener(self):
        pass

