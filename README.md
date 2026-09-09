# ReSearchAI

A scaffold for an AI‑powered research mentor.

## Architecture

- **Streamlit** – Front‑end UI
- **FastAPI** – Backend API
- **LangGraph** – Agent orchestration layer (future)
- **n8n** – Future automation/integration layer (not part of current scaffold)

## Project Structure

```
ReSearchAI/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── discovery.py
│   │   ├── analysis.py
│   │   ├── gap_analysis.py
│   │   ├── critic.py
│   │   └── roadmap.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── research_graph.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── research.py
│   ├── tools/__init__.py
│   └── rag/__init__.py
│
├── frontend/
│   ├── __init__.py
│   └── app.py
│
├── n8n/workflows/
│
├── tests/
│   ├── __init__.py
│   ├── test_backend.py
│   └── test_graph.py
│
├── .gitignore
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Setup

```bash
# Create virtual environment
python -m venv venv
# Windows activation
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy example)
copy .env.example .env
```

## Run Services

```bash
# FastAPI backend (default port 8000)
uvicorn backend.main:app --reload

# Streamlit UI (default port 8501)
streamlit run frontend/app.py
```

## Tests

```bash
pytest -q
```

## Next Steps

- Implement the six specialized agents inside `backend/agents/`
- Add real LLM calls, Semantic Scholar and arXiv integrations
- Extend LangGraph with conditional routing and loops
- Add RAG and vector database support
- Build n8n workflows for automation
```
