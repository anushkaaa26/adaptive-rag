# Adaptive RAG - Agentic AI Chatbot

An intelligent, end-to-end Retrieval-Augmented Generation (RAG) system powered by
agentic AI architecture, combining dynamic query routing, document retrieval, and
LLM generation via LangGraph, FastAPI, Qdrant, and Streamlit.

## Quick Start

### Option A: Local

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# edit .env with your OpenAI / Tavily / Qdrant / MongoDB credentials

# 3. Run the backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4. Run the frontend (separate terminal)
cd streamlit_app
streamlit run home.py
```

### Option B: Docker Compose

```bash
cp .env.example .env   # fill in OpenAI / Tavily keys
docker compose up --build
```

This starts MongoDB, Qdrant, the FastAPI backend, and the Streamlit frontend
together, wired to talk to each other automatically.

- API docs: http://localhost:8000/docs
- Web app: http://localhost:8501

## Authentication

The Streamlit app has a real login/register flow backed by `/auth/register`
and `/auth/login`. Passwords are hashed with bcrypt and stored in MongoDB
(with an in-memory fallback if MongoDB isn't reachable, for local dev without
a database).

## Testing

```bash
pip install -r requirements.txt
pytest
```

Tests cover the pure-function routing/decision logic, shared utilities, and
Pydantic models — no API keys or live services required.

## Project Structure

```
AdaptiveRag/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/                       # routes.py (rag), auth_routes.py (login/register)
│   ├── auth/service.py            # bcrypt password hashing, Mongo-backed user store
│   ├── config/                    # settings.py, prompts.yaml
│   ├── core/                      # config re-export, logger
│   ├── db/mongo_client.py         # Motor (async MongoDB) client
│   ├── llms/openai.py             # ChatOpenAI initialization
│   ├── memory/                    # Mongo + in-memory chat history
│   ├── models/                    # Pydantic + TypedDict schemas (incl. user.py)
│   ├── rag/                       # graph_builder, nodes, retriever, upload, ReAct agent
│   └── tools/                     # shared helpers, routing decisions
├── streamlit_app/
│   ├── home.py                    # Login / register UI
│   ├── pages/chat.py               # Chat + document upload UI
│   ├── utils/api_client.py         # Backend HTTP client
│   └── Dockerfile
├── tests/                          # pytest unit tests (pure-function logic)
├── Dockerfile                       # Backend image
├── docker-compose.yml               # Mongo + Qdrant + backend + frontend
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── LICENSE
├── CODE_STYLE_GUIDE.md
├── QUICK_REFERENCE.md
├── VERIFICATION_CHECKLIST.md
└── DOCUMENTATION_INDEX.md
```

## How Routing Works

Each query is classified as one of:
- **index** → retrieved from your uploaded documents (Qdrant)
- **general** → answered directly from the LLM's general knowledge
- **search** → answered using real-time Tavily web search

Retrieved documents are graded for relevance; if none are relevant, the query is
rewritten and retried, then falls back to web search after a couple of attempts.

## Answer Verification

After generation, an additional `verify` node checks whether the answer is
actually grounded in the retrieved context (using the `VerificationResult`
model). If it isn't, and retries remain, the graph loops back through
rewrite/retrieval; otherwise a disclaimer is appended to the final answer.

## Notes

This is a complete, runnable implementation matching the architecture described
in the original project README, including authentication, Docker packaging,
and a test suite. You'll need your own OpenAI, Tavily, and Qdrant (and
optionally MongoDB) credentials/instances to run it end-to-end — those are the
only pieces that can't be stubbed out.
