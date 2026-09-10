# backend/graph/state.py

"""LangGraph state definition for ReSearchAI.
Only includes fields needed for the scaffold; will be extended later.
"""

from typing import TypedDict, List, Dict, Any, Optional

class ResearchState(TypedDict, total=False):
    # Input fields
    user_topic: str
    experience_level: str
    user_interest: Optional[str]

    # Intermediate results (placeholders)
    research_plan: Optional[Dict[str, Any]]
    search_queries: Optional[List[str]]
    papers: Optional[List[Dict[str, Any]]]
    selected_papers: Optional[List[Dict[str, Any]]]
    analyzed_papers: Optional[List[Dict[str, Any]]]
    analysis_results: Optional[List[Dict[str, Any]]]
    gaps: Optional[List[Dict[str, Any]]]
    research_gaps: Optional[List[Dict[str, Any]]]
    critique: Optional[Dict[str, Any]]
    research_questions: Optional[List[str]]
    roadmap: Optional[Dict[str, Any]]
    planner_output: Optional[Dict[str, Any]]

    # Misc
    errors: Optional[List[str]]
    workflow_status: Optional[str]
