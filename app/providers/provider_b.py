from groq import Groq

from app.config.settings import (
    PROVIDER_B_API_KEY,
    PROVIDER_B_MODEL,
)
from app.providers.base import LLMProvider


class ProviderB(LLMProvider):

    def __init__(self):
        if not PROVIDER_B_API_KEY:
            raise ValueError(
                "PROVIDER_B_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=PROVIDER_B_API_KEY
        )
        self.model_name = PROVIDER_B_MODEL

    async def generate(self, query: str) -> str:
        response = self.client.chat.completions.create(
            model=PROVIDER_B_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
        )

        return response.choices[0].message.content