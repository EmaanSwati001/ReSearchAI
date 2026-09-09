# backend/graph/research_graph.py

"""Construction of the LangGraph research workflow.
All nodes are placeholders that simply pass the state through.
The graph is linear for now:
planner -> discovery -> analysis -> gap_analysis -> critic -> roadmap -> finalize
"""

from typing import Dict, Any

from langgraph.graph import StateGraph

# Import placeholder agent functions
from backend.agents.planner import run as planner_run
from backend.agents.discovery import run as discovery_run
from backend.agents.analysis import run as analysis_run
from backend.agents.gap_analysis import run as gap_analysis_run
from backend.agents.critic import run as critic_run
from backend.agents.roadmap import run as roadmap_run

def finalize(state: Dict[str, Any]) -> Dict[str, Any]:
    """Final node that marks the workflow as complete.
    In a real implementation this would collect and format results.
    """
    state.setdefault("status", "success")
    return state

def get_research_graph() -> StateGraph:
    """Create and return a LangGraph StateGraph for the research pipeline.
    Returns:
        StateGraph: Configured graph ready for .invoke(initial_state).
    """
    graph = StateGraph(state_schema=None)  # We will not enforce a schema here.

    # Add nodes – each node is a callable that receives and returns a state dict.
    graph.add_node("planner", planner_run)
    graph.add_node("discovery", discovery_run)
    graph.add_node("analysis", analysis_run)
    graph.add_node("gap_analysis", gap_analysis_run)
    graph.add_node("critic", critic_run)
    graph.add_node("roadmap", roadmap_run)
    graph.add_node("finalize", finalize)

    # Define linear edges
    graph.add_edge("planner", "discovery")
    graph.add_edge("discovery", "analysis")
    graph.add_edge("analysis", "gap_analysis")
    graph.add_edge("gap_analysis", "critic")
    graph.add_edge("critic", "roadmap")
    graph.add_edge("roadmap", "finalize")

    # Set start and end
    graph.set_entry_point("planner")
    graph.set_finish_point("finalize")

    return graph.compile()
