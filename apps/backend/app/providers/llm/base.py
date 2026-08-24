from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):

    @abstractmethod
    def list_models(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
    ) -> str:
        raise NotImplementedError