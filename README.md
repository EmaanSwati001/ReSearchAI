# ReSearchAI

ReSearchAI is an AI research mentor that helps students move from a broad research topic to an evidence-backed research direction and actionable research roadmap.

## What ReSearchAI Does

Instead of simply dumping links to research papers, ReSearchAI automatically analyzes the literature, identifies genuine research gaps across multiple papers, critically evaluates those gaps for validity, and produces a concrete, step-by-step research plan. 

## Architecture

ReSearchAI is built on a modern AI agent architecture:

Streamlit UI
↓
FastAPI Backend
↓
LangGraph Orchestrator
↓
Specialized Research Agents
↓
Research APIs (Semantic Scholar, arXiv) + RAG

## Agent Pipeline

The LangGraph workflow orchestrates the following specialized agents:

1. **Planner**: Parses the user's broad topic and generates a structured research plan.
2. **Discovery**: Queries academic databases (Semantic Scholar, arXiv) to find relevant research papers and deduplicates them.
3. **Paper Analysis + RAG**: Implements a local Retrieval-Augmented Generation (RAG) system to ground analysis. It chunks paper content, stores it in a FAISS vector index, retrieves evidence relevant to the research queries, and extracts methodologies and limitations.
4. **Gap Analysis**: Compares findings across multiple papers to identify unaddressed research gaps.
5. **Research Critic**: Acts as a skeptical mentor, evaluating whether the proposed gaps are genuinely supported by the retrieved evidence.
6. **Research Roadmap**: Converts the strongest, validated research gap into an actionable, step-by-step roadmap for a student.

## RAG (Retrieval-Augmented Generation)

To ensure the AI does not hallucinate paper contents, ReSearchAI uses a fully local RAG pipeline:
- Discovered papers are collected and chunked.
- Embeddings are generated locally using `sentence-transformers` (`all-MiniLM-L6-v2`).
- Vectors are stored and searched using `faiss-cpu`.
- Relevant evidence snippets are retrieved and injected into the LLM prompt.
- The LLM grounds its analysis strictly in the retrieved evidence.

*Note: The project uses Groq for fast LLM inference and does not require an OpenAI API key.*

## Technologies

- **Backend**: FastAPI, Python 3
- **Frontend**: Streamlit
- **Orchestration**: LangGraph, Langchain
- **AI/LLM**: Groq API
- **Embeddings/Vector Store**: `sentence-transformers`, `faiss-cpu`

## Setup

1. **Clone the repository.**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

Copy `.env.example` to `.env` and fill in the required keys:

- `GROQ_API_KEY`: Your Groq API key for the LLM.
- `GROQ_MODEL`: Recommended to use `llama3-8b-8192` or `llama3-70b-8192`.
- `SEMANTIC_SCHOLAR_API_KEY`: (Optional) Provides higher rate limits for discovery.

## Run Locally

**Start the FastAPI Backend:**
```bash
uvicorn backend.main:app --reload
```

**Start the Streamlit Frontend (in a new terminal):**
```bash
streamlit run frontend/app.py
```

## Docker

You can easily run the entire stack using Docker Compose:

```bash
docker-compose up --build
```
This will expose the backend at `http://localhost:8000` and the frontend at `http://localhost:8501`.

## Project Structure

```
backend/
    agents/      # Specialized LangGraph nodes (planner, discovery, etc.)
    rag/         # Local RAG implementation (loader, chunker, retriever, vector_store)
    schemas/     # Pydantic models for structured data
    graph/       # LangGraph state and orchestration
    main.py      # FastAPI entrypoint
frontend/
    app.py       # Streamlit UI
tests/           # Comprehensive pytest suite
```

## Research Workflow

The system progresses logically through these stages:

**Topic** → **Plan** → **Papers** → **Evidence** → **Analysis** → **Gaps** → **Critic** → **Roadmap**
