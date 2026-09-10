# backend/schemas/gap.py

"""Pydantic schema for Research Gap (Phase 5).

Represents a research gap, contradiction, or opportunity identified
by cross-comparing analyzed papers.
"""

from typing import List, Union
from pydantic import BaseModel, Field, field_validator


class ResearchGap(BaseModel):
    """Structured representation of an identified research gap."""

    gap: str = Field(
        ..., description="A concise, cautious description of the potential research gap"
    )
    evidence: str = Field(
        ..., description="Specific evidence from the analyzed papers supporting this observation"
    )
    supporting_papers: List[str] = Field(
        default_factory=list,
        description="List of paper IDs or titles from the sample that support this gap"
    )
    gap_type: str = Field(
        ...,
        description="Category of the gap (e.g. Dataset Gap, Methodology Gap, Evaluation Gap, Application Gap, Contradiction, Limitation Gap)"
    )
    confidence: str = Field(
        ..., description="Confidence level based on available evidence: High, Medium, or Low"
    )
    research_opportunity: str = Field(
        ..., description="A concrete direction or question a researcher could investigate"
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Union[str, None]) -> str:
        if not v:
            return "Medium"
        v_str = str(v).strip().capitalize()
        if v_str in ("High", "Medium", "Low"):
            return v_str
        if "high" in str(v).lower():
            return "High"
        if "low" in str(v).lower():
            return "Low"
        return "Medium"

    @field_validator("supporting_papers", mode="before")
    @classmethod
    def normalize_supporting_papers(cls, v: Union[List[str], str, None]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return []

    @field_validator("gap", "evidence", "gap_type", "research_opportunity", mode="before")
    @classmethod
    def normalize_text_fields(cls, v: Union[str, List[str], None]) -> str:
        if v is None:
            return ""
        if isinstance(v, list):
            return "; ".join(str(item).strip() for item in v if str(item).strip())
        return str(v).strip()
