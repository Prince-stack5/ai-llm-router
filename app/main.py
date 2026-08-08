from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Intelligent LLM Router",
    description="AI-powered API router that selects the best LLM provider.",
    version="1.0.0",
)

app.include_router(
    router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "Intelligent LLM Router is running"
    }