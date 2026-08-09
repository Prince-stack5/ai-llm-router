import json
from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.config.settings import (
    PROVIDER_A_API_KEY,
    CLASSIFIER_MODEL,
)


class ClassificationResult(BaseModel):
    category: str = Field(description="The predicted category of the user query.")
    confidence: float = Field(description="The confidence score between 0.0 and 1.0.")


TaskType = Literal[
    "Coding",
    "Mathematics",
    "Reasoning",
    "Translation",
    "Summarization",
    "Email Writing",
    "Creative Writing",
    "General Knowledge",
    "Explanation / Education",
    "Analysis",
    "Data / SQL",
    "Web / Research",
    "Planning",
    "Conversation",
    "Document / Content Generation",
]

VALID_CATEGORIES = {
    "Coding": "Coding",
    "Mathematics": "Mathematics",
    "Reasoning": "Reasoning",
    "Translation": "Translation",
    "Summarization": "Summarization",
    "Email Writing": "Email Writing",
    "Creative Writing": "Creative Writing",
    "General Knowledge": "General Knowledge",
    "Explanation / Education": "Explanation / Education",
    "Analysis": "Analysis",
    "Data / SQL": "Data / SQL",
    "Web / Research": "Web / Research",
    "Planning": "Planning",
    "Conversation": "Conversation",
    "Document / Content Generation": "Document / Content Generation",
}


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

- Coding
- Mathematics
- Reasoning
- Translation
- Summarization
- Email Writing
- Creative Writing
- General Knowledge
- Explanation / Education
- Analysis
- Data / SQL
- Web / Research
- Planning
- Conversation
- Document / Content Generation

Definitions:

Coding:
Programming, debugging, software development, algorithms, APIs, or technical implementation.

Mathematics:
Solving math problems, equations, calculus, algebra, numerical reasoning.

Reasoning:
Logical reasoning, puzzles, multi-step problem solving, deduction, or complex analysis.

Translation:
Translating text from one language to another.

Summarization:
Summarizing, shortening, extracting key points, or condensing existing information.

Email Writing:
Drafting emails, letters, professional communications, out-of-office replies.

Creative Writing:
Poetry, stories, plays, scripts, marketing copy, brainstorming ideas.

General Knowledge:
Trivia, historical facts, scientific questions, general informational queries.

Explanation / Education:
Explaining concepts, teaching, tutorials, "how does X work" type queries.

Analysis:
Comparing options, analyzing data, summarizing research findings, trade-off analysis.

Data / SQL:
Writing SQL queries, database schema design, formatting JSON/CSV data.

Web / Research:
Searching the web, finding sources, reviewing current events.

Planning:
Creating itineraries, schedules, project plans, task lists.

Conversation:
General chitchat, greeting, friendly dialog, basic interaction.

Document / Content Generation:
Creating long-form documents, reports, essays, outlines, templates.

Return ONLY valid JSON:

{{
    "category": "Coding",
    "confidence": 0.95
}}

User query:

{query}
"""

        try:
            response = self.client.models.generate_content(
                model=CLASSIFIER_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClassificationResult,
                )
            )

            res_text = ""
            if hasattr(response, 'text') and response.text:
                res_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                parts = response.candidates[0].content.parts
                res_text = "".join([part.text for part in parts if hasattr(part, 'text') and part.text])

            result = json.loads(res_text)

            category = result.get(
                "category",
                "General Knowledge"
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.5
                )
            )

            # Case-insensitive lookup mapping
            lookup = {k.lower(): v for k, v in VALID_CATEGORIES.items()}
            
            # Map legacy or approximate categories
            legacy_mappings = {
                "writing": "Creative Writing",
                "general": "General Knowledge",
                "math": "Mathematics"
            }
            
            cleaned_category = category.strip().lower()
            if cleaned_category in lookup:
                category = lookup[cleaned_category]
            elif cleaned_category in legacy_mappings:
                category = legacy_mappings[cleaned_category]
            else:
                category = "General Knowledge"

            confidence = max(
                0.0,
                min(confidence, 1.0)
            )

            return category, confidence

        except (json.JSONDecodeError, ValueError, TypeError):

            return "General Knowledge", 0.0