from abc import ABC, abstractmethod
from typing import Any

class InputFormat(ABC):

    @abstractmethod
    def read(self, content: str) -> Any:
        pass