from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.router.classifier import QueryClassifier
from app.router.router import LLMRouter


router = APIRouter()

llm_router = LLMRouter()
classifier = QueryClassifier()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
async def chat(request: ChatRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    task, confidence = await classifier.classify(
        request.query
    )

    provider_name, provider = (
        llm_router.select_provider(task)
    )

    fallback_used = False

    try:

        response = await provider.generate(
            request.query
        )

    except Exception as primary_error:

        fallback_used = True

        fallback_name, fallback_provider = (
            llm_router.get_fallback(
                provider_name
            )
        )

        try:

            response = await fallback_provider.generate(
                request.query
            )

            provider_name = fallback_name

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

    return {
        "query": request.query,
        "task": task,
        "confidence": confidence,
        "provider": provider_name,
        "fallback_used": fallback_used,
        "response": response,
    }