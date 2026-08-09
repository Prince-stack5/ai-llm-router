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
            # New Capitalized categories
            "Coding": "provider_a",
            "Mathematics": "provider_a",
            "Reasoning": "provider_b",
            "Translation": "provider_b",
            "Summarization": "provider_a",
            "Email Writing": "provider_b",
            "Creative Writing": "provider_b",
            "General Knowledge": "provider_a",
            "Explanation / Education": "provider_a",
            "Analysis": "provider_a",
            "Data / SQL": "provider_a",
            "Web / Research": "provider_a",
            "Planning": "provider_b",
            "Conversation": "provider_b",
            "Document / Content Generation": "provider_a",
            
            # Legacy lowercase categories (fallback)
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