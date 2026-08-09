from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from app.router.classifier import QueryClassifier
from app.router.router import LLMRouter


router = APIRouter()

llm_router = LLMRouter()
classifier = QueryClassifier()


class ChatRequest(BaseModel):
    query: str
    provider: Optional[str] = "auto"


@router.post("/chat")
async def chat(request: ChatRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    start_time = time.perf_counter()

    # Measure classification time
    class_start = time.perf_counter()
    try:
        task, confidence = await classifier.classify(
            request.query
        )
    except Exception as e:
        print(f"Classification failed: {e}. Falling back to default task 'general'")
        task, confidence = "general", 0.5
    classification_latency = time.perf_counter() - class_start

    # Determine provider (check manual override first)
    if request.provider and request.provider.lower() in ["provider_a", "provider_b"]:
        provider_name = request.provider.lower()
        provider = llm_router.providers[provider_name]
    else:
        provider_name, provider = (
            llm_router.select_provider(task)
        )

    fallback_used = False
    actual_model = getattr(provider, "model_name", "unknown")
    gen_start = time.perf_counter()

    try:
        response = await provider.generate(
            request.query
        )
        generation_latency = time.perf_counter() - gen_start

    except Exception as primary_error:
        fallback_used = True

        fallback_name, fallback_provider = (
            llm_router.get_fallback(
                provider_name
            )
        )
        actual_model = getattr(fallback_provider, "model_name", "unknown")

        try:
            response = await fallback_provider.generate(
                request.query
            )
            provider_name = fallback_name
            generation_latency = time.perf_counter() - gen_start

        except Exception as fallback_error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "All LLM providers failed.",
                    "primary_provider": provider_name,
                    "primary_error": str(primary_error),
                    "fallback_error": str(fallback_error),
                }
            )

    total_latency = time.perf_counter() - start_time

    return {
        "query": request.query,
        "task": task,
        "confidence": confidence,
        "provider": provider_name,
        "model": actual_model,
        "fallback_used": fallback_used,
        "response": response,
        "metrics": {
            "classification_latency": round(classification_latency, 3),
            "generation_latency": round(generation_latency, 3),
            "total_latency": round(total_latency, 3)
        }
    }