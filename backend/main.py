# backend/main.py

"""FastAPI entry point for ReSearchAI.
Provides minimal health and research endpoints.
"""

from fastapi import FastAPI, HTTPException
import backend.config  # loads .env variables
from backend.schemas.research import ResearchRequest, ResearchResponse
from backend.graph.research_graph import get_research_graph

app = FastAPI(title="ReSearchAI Backend")

@app.get("/")
def root():
    return {"message": "ReSearchAI API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest):
    # Initialize the LangGraph workflow with the request data.
    graph = get_research_graph()
    # Prepare initial state dictionary.
    initial_state = {
        "user_topic": request.topic,
        "experience_level": request.experience_level,
        "user_interest": request.interest,
    }
    # Run the graph synchronously.
    try:
        result = graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Build the response from the graph result.
    return ResearchResponse(
        status=result.get("status", "success"),
        planner_output=result.get("planner_output"),
        papers=result.get("papers"),
        analysis_results=result.get("analysis_results"),
        gaps=result.get("gaps"),
        critic_results=result.get("critic_results"),
        roadmap=result.get("roadmap"),
    )
