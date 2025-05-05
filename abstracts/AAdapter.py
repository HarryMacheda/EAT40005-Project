from abc import ABC, abstractmethod
from typing import TypeVar, Generic 

# Type variables
T = TypeVar('T')  # Decoded
U = TypeVar('U')  # Encoded

# Data adapter abstract class
class AAdapter(ABC, Generic[T, U]):
    @staticmethod
    @abstractmethod
    def Encode(input:T) -> U:
        pass

    @staticmethod
    @abstractmethod
    def Decode(input:U) -> T:
        pass