# Quick Reference

## Local development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in credentials

# Backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd streamlit_app && streamlit run home.py
```

## Docker

```bash
docker compose up --build
```
Starts MongoDB, Qdrant, the FastAPI backend (port 8000), and Streamlit
frontend (port 8501) together.

## Tests

```bash
pytest
```

## Common endpoints

| Method | Path                          | Purpose                        |
|--------|-------------------------------|---------------------------------|
| POST   | `/auth/register`              | Create a new user account       |
| POST   | `/auth/login`                 | Authenticate a user             |
| POST   | `/rag/query`                  | Submit a query to the RAG agent |
| POST   | `/rag/documents/upload`       | Upload + index a PDF/TXT file   |
| GET    | `/rag/history/{session_id}`   | Fetch chat history for a session|
| GET    | `/health`                     | Liveness + MongoDB connectivity |

## Environment variables

See `.env.example` for the full list (OpenAI, Tavily, Qdrant, MongoDB).
