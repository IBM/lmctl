from abc import ABC, abstractmethod
from typing import List, Any

class OutputFormat(ABC):

    @abstractmethod
    def convert_list(self, element_list: List[Any]) -> str:
        pass

    @abstractmethod
    def convert_element(self, element: Any) -> str:
        pass
