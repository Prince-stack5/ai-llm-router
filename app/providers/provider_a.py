from google import genai

from app.config.settings import (
    PROVIDER_A_API_KEY,
    PROVIDER_A_MODEL,
)
from app.providers.base import LLMProvider


class ProviderA(LLMProvider):

    def __init__(self):
        if not PROVIDER_A_API_KEY:
            raise ValueError("PROVIDER_A_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=PROVIDER_A_API_KEY
        )
        self.model_name = PROVIDER_A_MODEL

    async def generate(self, query: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=PROVIDER_A_MODEL,
                contents=query,
            )

            return response.text or "No response received."

        except Exception as e:
            print(f"Provider A error: {e}")
            raise e