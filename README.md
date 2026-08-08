# AI LLM Router

A FastAPI-based intelligent LLM router that receives a user's query, understands what kind of task it is, and sends the request to the most suitable LLM provider.

The main goal of this project is to keep the API simple for the user while handling provider selection internally.

## What it does

The API accepts one query:

```http
POST /api/v1/chat
```

For example:

```json
{
  "query": "Write a Python function to reverse a string"
}
```

The system first classifies the query and then selects a provider.

Currently supported task types:

* Coding
* Writing
* Summarization
* Translation
* Reasoning
* General

## How it works

```text
User Query
    |
    v
FastAPI Endpoint
    |
    v
AI Query Classifier
    |
    v
Task Detection
    |
    v
LLM Router
   / \
  /   \
Gemini  Groq
  \     /
   \   /
  Response
```

The classifier uses Gemini to understand the user's request instead of depending only on keywords.

For example:

```text
"Write a Python function to reverse a string"
        ↓
coding
        ↓
Provider A
```

And:

```text
"Write a professional email asking for leave"
        ↓
writing
        ↓
Provider B
```

## Providers

### Provider A

Google Gemini

Used mainly for:

* Coding
* Summarization
* General queries

### Provider B

Groq

Used mainly for:

* Writing
* Translation
* Reasoning

The provider implementation is separated from the API code, so adding another provider does not require changing the main API logic.

## Fallback

If the selected provider fails, the router tries the other available provider.

For example:

```text
Provider A
   |
   X Failed
   |
   v
Provider B
   |
   v
Response
```

If both providers fail, the API returns a `502` response.

## API Response

A successful response looks like:

```json
{
  "query": "Write a Python function to reverse a string",
  "task": "coding",
  "confidence": 0.95,
  "provider": "provider_a",
  "fallback_used": false,
  "response": "..."
}
```

The response includes the selected task and provider so that the routing decision can be easily understood.

## Project Structure

```text
ai-llm-router/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── providers/
│   │   ├── base.py
│   │   ├── provider_a.py
│   │   └── provider_b.py
│   │
│   ├── router/
│   │   ├── classifier.py
│   │   └── router.py
│   │
│   ├── schemas/
│   │   └── chat.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_api.py
│   └── test_router.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

Clone the repository:

```bash
git clone <your-github-repository-url>
cd ai-llm-router
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root.

```env
PROVIDER_A_API_KEY=your_gemini_api_key
PROVIDER_B_API_KEY=your_groq_api_key

PROVIDER_A_MODEL=gemini-3.6-flash
PROVIDER_B_MODEL=llama-3.3-70b-versatile
CLASSIFIER_MODEL=gemini-3.6-flash
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

Tests are written using pytest.

Run:

```bash
pytest
```

The tests cover routing, API validation, fallback selection, and mocked provider responses.

The tests don't make real LLM API calls, so they can be run without consuming API credits.

## Why I built it this way

I wanted the API layer to remain independent from the actual LLM providers.

The API only receives the query. The classifier decides what the user is trying to do, and the router decides which provider should handle it.

Each provider follows the same interface, which makes it easier to add another provider later.

The fallback mechanism also prevents a temporary provider failure from immediately causing the whole request to fail.

## Future Improvements

Some things I would add with more time:

* More LLM providers
* Provider health checks
* Cost-based routing
* Response streaming
* Rate limiting
* Request logging and monitoring
* Authentication
* Token and latency tracking
* Caching

## Tech Stack

* Python
* FastAPI
* Google Gemini
* Groq
* Pydantic
* pytest
* Uvicorn
* python-dotenv

## Author

Prince Varshney
