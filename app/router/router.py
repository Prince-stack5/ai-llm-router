from app.providers.base import LLMProvider
from app.providers.provider_a import ProviderA
from app.providers.provider_b import ProviderB


class LLMRouter:

    def __init__(self):
        self.providers: dict[str, LLMProvider] = {
            "provider_a": ProviderA(),
            "provider_b": ProviderB(),
        }

    def select_provider(self, task: str) -> tuple[str, LLMProvider]:

        provider_map = {
            "coding": "provider_a",
            "summarization": "provider_a",
            "writing": "provider_b",
            "translation": "provider_b",
            "reasoning": "provider_b",
            "general": "provider_a",
        }

        provider_name = provider_map.get(task, "provider_a")

        return provider_name, self.providers[provider_name]

    def get_fallback(
        self,
        provider_name: str
    ) -> tuple[str, LLMProvider]:

        fallback_map = {
            "provider_a": "provider_b",
            "provider_b": "provider_a",
        }

        fallback_name = fallback_map[provider_name]

        return fallback_name, self.providers[fallback_name]