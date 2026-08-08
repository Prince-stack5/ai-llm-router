import json
from typing import Literal

from google import genai

from app.config.settings import (
    PROVIDER_A_API_KEY,
    CLASSIFIER_MODEL,
)


TaskType = Literal[
    "coding",
    "writing",
    "summarization",
    "translation",
    "reasoning",
    "general",
]


class QueryClassifier:

    def __init__(self):
        if not PROVIDER_A_API_KEY:
            raise ValueError(
                "PROVIDER_A_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=PROVIDER_A_API_KEY
        )

    async def classify(self, query: str) -> tuple[TaskType, float]:

        prompt = f"""
You are an API routing classifier.

Classify the user's request into exactly ONE of these categories:

- coding
- writing
- summarization
- translation
- reasoning
- general

Definitions:

coding:
Programming, debugging, software development,
algorithms, databases, APIs, or technical implementation.

writing:
Emails, essays, stories, articles, captions,
rewriting, professional communication, or creative writing.

summarization:
Summarizing, shortening, extracting key points,
or condensing existing information.

translation:
Translating text from one language to another.

reasoning:
Analysis, comparison, problem solving,
decision making, explanations, or logical reasoning.

general:
Anything that doesn't clearly fit the categories above.

Return ONLY valid JSON:

{{
    "category": "coding",
    "confidence": 0.95
}}

User query:

{query}
"""

        response = self.client.models.generate_content(
           model=CLASSIFIER_MODEL,
            contents=prompt,
        )

        try:
            result = json.loads(response.text)

            category = result.get(
                "category",
                "general"
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.5
                )
            )

            valid_categories = {
                "coding",
                "writing",
                "summarization",
                "translation",
                "reasoning",
                "general",
            }

            if category not in valid_categories:
                category = "general"

            confidence = max(
                0.0,
                min(confidence, 1.0)
            )

            return category, confidence

        except (json.JSONDecodeError, ValueError, TypeError):

            return "general", 0.0