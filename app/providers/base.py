from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    async def generate(self, query: str) -> str:
        """
        Generate a response from the LLM provider.
        """
        pass