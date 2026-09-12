# backend/schemas/roadmap.py

"""Pydantic schema for the Research Roadmap Agent (Phase 8).

Represents an actionable research plan generated from evaluated gaps.
"""

from typing import List
from pydantic import BaseModel, Field, conint

class RoadmapResult(BaseModel):
    """Actionable research plan generated from evaluated gaps."""

    research_direction: str = Field(..., description="The main research direction or chosen gap.")
    objective: str = Field(..., description="Clear and measurable research objective.")
    research_questions: List[str] = Field(default_factory=list, description="Specific research questions to answer.")
    methodology: List[str] = Field(default_factory=list, description="Step-by-step methodology.")
    data_requirements: List[str] = Field(default_factory=list, description="Required datasets or data sources.")
    implementation_steps: List[str] = Field(default_factory=list, description="Step-by-step implementation plan.")
    evaluation_metrics: List[str] = Field(default_factory=list, description="Metrics to evaluate the research outcome.")
    expected_challenges: List[str] = Field(default_factory=list, description="Potential challenges and risks.")
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected contributions and outcomes.")
    validation_steps: List[str] = Field(default_factory=list, description="Steps to validate the gap (especially if partially supported/weak).")
    timeline_weeks: int = Field(..., ge=1, description="Expected timeline in weeks (must be positive integer).")
