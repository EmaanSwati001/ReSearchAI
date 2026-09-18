# backend/main.py

"""FastAPI entry point for ReSearchAI.
Provides minimal health and research endpoints.
"""

import time
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
import backend.config  # loads .env variables
from backend.schemas.research import ResearchRequest, ResearchResponse
from backend.graph.research_graph import get_research_graph

# Configure structured observability logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ReSearchAI.Backend")

app = FastAPI(title="ReSearchAI Backend", description="Multi-Agent Autonomous Research Intelligence Engine")

@app.get("/")
def root():
    return {"message": "ReSearchAI API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest):
    logger.info("Received research request for topic: '%s' (Level: %s, Focus: %s)",
                request.topic, request.experience_level, request.interest)
    start_time = time.time()
    
    # Initialize the LangGraph workflow with the request data.
    graph = get_research_graph()
    initial_state = {
        "user_topic": request.topic,
        "experience_level": request.experience_level,
        "user_interest": request.interest,
    }
    
    # Run the graph synchronously.
    try:
        result = graph.invoke(initial_state)
        latency = time.time() - start_time
        logger.info("LangGraph pipeline successfully finished in %.2fs for topic '%s'", latency, request.topic)
    except Exception as exc:
        latency = time.time() - start_time
        logger.error("LangGraph pipeline failed after %.2fs: %s", latency, exc)
        traceback.print_exc()
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

