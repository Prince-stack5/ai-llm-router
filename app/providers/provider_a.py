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

    async def generate(self, query: str) -> str:
        response = self.client.models.generate_content(
          model=PROVIDER_A_MODEL,
            contents=query,
        )

        return response.text