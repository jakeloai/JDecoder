from abc import ABC, abstractmethod
from typing import Optional


class DecodeMethod(ABC):
    name: str = ""

    @abstractmethod
    def decode(self, data: str) -> Optional[str]:
        pass

    @abstractmethod
    def encode(self, data: str) -> str:
        pass

    def can_decode(self, data: str) -> bool:
        return True
