# 🎓 ReSearchAI: Autonomous AI Research Mentor & Roadmap Synthesizer

> **Atomcamp Agentic AI Bootcamp — Final Capstone Project**  
> An autonomous multi-agent platform powered by **LangGraph**, **Groq LLMs**, **FAISS RAG**, **Semantic Scholar**, **arXiv**, and **Streamlit**.

---

## 🌟 Overview & Problem Statement

Students and early-stage researchers often struggle to transition from a broad research topic to a well-formulated, novel research direction. Existing tools either dump hundreds of paper links without synthesis or generate hallucinated research ideas unsupported by scientific literature.

**ReSearchAI** solves this by orchestrating **7 specialized AI agents**:
1. **Planner Agent**: Structures the initial research scope, subtopics, and questions.
2. **Discovery Agent**: Automatically queries academic databases (**Semantic Scholar** & **arXiv**) and deduplicates paper literature.
3. **Local Vector RAG Engine**: Chunks paper abstracts/full-texts, generates local embeddings (`all-MiniLM-L6-v2`), and indexes them in a **FAISS** vector store.
4. **Paper Analysis Agent**: Extracts factual methodologies, datasets, findings, and limitations strictly grounded in retrieved RAG evidence.
5. **Gap Analysis Agent**: Performs cross-paper meta-analysis to discover unaddressed research gaps across literature.
6. **Research Critic Agent**: Acts as a skeptical peer reviewer, rigorously evaluating evidence strength and potential flaws in proposed gaps.
7. **Roadmap Synthesis Agent**: Converts validated research gaps into a practical, step-by-step 4–8 week execution plan for students.

---

## 🏗️ Multi-Agent System Architecture

```mermaid
graph TD
    User([User Request / Topic]) --> UI[Streamlit Capstone UI]
    UI --> API[FastAPI Backend Server]
    API --> Orchestration[LangGraph State Machine]

    subgraph Agent Pipeline Workflow
        Orchestration --> Agent1[1. Planner Agent 🧠]
        Agent1 --> Agent2[2. Discovery Agent 🔍]
        
        subgraph External Literature APIs
            Agent2 --> SS[Semantic Scholar API]
            Agent2 --> ArXiv[arXiv Atom API]
        end
        
        Agent2 --> Agent3[3. Local RAG & Vector Engine 📚]
        Agent3 --> FAISS[(FAISS Vector Index)]
        
        Agent3 --> Agent4[4. Paper Analysis Agent 📊]
        Agent4 --> Agent5[5. Gap Analysis Agent 🔎]
        Agent5 --> Agent6[6. Research Critic Agent 🧑‍🏫]
        Agent6 --> Agent7[7. Roadmap Synthesis Agent 🗺️]
    end

    Agent7 --> Response[Structured JSON Dossier]
    Response --> UI
```

---

## 📝 Agent Prompt Design & Engineering

Each agent in the pipeline uses strict prompt engineering strategies to eliminate hallucinations and enforce scientific rigor:

| Agent | Prompt Design Strategy | Primary Output Schema |
| :--- | :--- | :--- |
| **Planner Agent** | System persona as an academic research director. Forces pure JSON output detailing title, subtopics, research questions, and methodology. | `PlannerOutput` |
| **Paper Analysis (RAG)** | Enforces strict **In-Context Grounding Rules**. Mandates `"Not specified in available evidence"` for missing data; forbids external background hallucination. | `PaperAnalysis` |
| **Gap Analysis Agent** | Requires cross-paper meta-comparison. Enforces cautious scientific claims (e.g. *"In this sample..."*) and categorizes gaps (Dataset, Methodology, Evaluation). | `ResearchGap` |
| **Research Critic Agent** | Skeptical reviewer persona. Instructed **not** to accept gaps automatically; assigns verdicts (*Supported*, *Partially Supported*, *Weak*) and explicit concerns. | `CriticResult` |
| **Roadmap Synthesis Agent** | Translates evaluated gaps into actionable student milestones: direction, objectives, timeline, step-by-step implementation, metrics, and risks. | `RoadmapResult` |

---

## 🛠️ Technology Stack

- **Orchestration**: LangGraph, LangChain
- **LLM Inference**: Groq API (`qwen/qwen3.8-27b` / `llama3-70b-8192`)
- **Embeddings & Vector Store**: `sentence-transformers` (`all-MiniLM-L6-v2`), `faiss-cpu`
- **External APIs**: Semantic Scholar Academic Graph API, arXiv Atom Query API
- **Backend API**: FastAPI, Uvicorn, Pydantic v2
- **Frontend Dashboard**: Streamlit (with Custom Theme & Multi-Agent Status Visualizer)
- **Testing & Quality**: Pytest (56 Unit & Integration Tests)
- **DevOps**: Docker, Docker Compose

---

## 🚀 Installation & Local Setup

### 1. Clone & Environment Setup

```bash
git clone https://github.com/your-username/ReSearchAI.git
cd ReSearchAI

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
SEMANTIC_SCHOLAR_API_KEY=optional_semantic_scholar_key
```

### 3. Run Application

**Terminal 1 — FastAPI Backend:**
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Streamlit Frontend:**
```bash
python -m streamlit run frontend/app.py --server.port 8501
```

Access the Streamlit Dashboard at [**http://localhost:8501**](http://localhost:8501).

---

## 🔍 Observability & Tracing

ReSearchAI provides end-to-end observability across the multi-agent pipeline:

1. **Structured Application Logging**:
   - Built-in Python standard logging with UTC timestamps, agent module names, and pipeline execution latencies in seconds.
   - Logs request payloads, API retry backoffs (e.g. Groq 429 mitigation), and error stack traces.

2. **LangSmith Tracing Integration**:
   - Native integration with LangChain / LangSmith tracing.
   - To enable full cloud tracing of agent thought graphs, add your keys to `.env`:
     ```env
     LANGCHAIN_TRACING_V2=true
     LANGCHAIN_API_KEY=your_langsmith_api_key_here
     LANGCHAIN_PROJECT=ReSearchAI
     ```

---

## 🐳 Docker Deployment & Docker Hub

### Run with Docker Compose (Recommended)

```bash
# 1. Copy environment template and add your GROQ_API_KEY
cp .env.example .env

# 2. Build and launch services
docker compose up --build
```
- **Backend API**: `http://localhost:8000`
- **Frontend Studio**: `http://localhost:8501`

### Docker Hub Deployment (Optional)

To publish and pull pre-built container images:
```bash
# Build & tag image
docker build -t <your-dockerhub-username>/researchai:latest .

# Push to Docker Hub
docker push <your-dockerhub-username>/researchai:latest
```

---

## 🧪 Automated Testing

ReSearchAI includes a comprehensive test suite (56 tests) covering Pydantic schemas, agent node execution, RAG vector retrieval, and backend endpoints.

```bash
python -m pytest
```

---

## 📜 Capstone Submission Deliverables

| Deliverable | Description | Location / Status |
| :--- | :--- | :--- |
| **1. GitHub Repo** | Clean code, modular structure, passing tests, and architecture documentation. | [GitHub Repository URL](https://github.com/) |
| **2. Demo Video** | 2–5 minute walkthrough: Problem statement, live multi-agent demo, and technical retrospective. | [Demo Video Link (Google Drive / Loom / YouTube)]() |
| **3. Live App / Docker** | Container steps (`docker compose up`) or Docker Hub image link. | `docker compose up --build` |

