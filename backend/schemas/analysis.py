# backend/schemas/analysis.py

"""Pydantic schema for Paper Analysis Agent (Phase 4).

Represents the structured analysis extracted from a paper's title and abstract.
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator


class PaperAnalysis(BaseModel):
    """Structured analysis for a single research paper."""

    paper_id: Optional[str] = Field(None, description="Identifier of the paper (arXiv ID or Semantic Scholar ID)")
    title: Optional[str] = Field(None, description="Title of the paper")
    research_problem: str = Field(
        ..., description="The core research problem or objective of the paper"
    )
    methodology: str = Field(
        ..., description="Methodology, techniques, and experimental setup used"
    )
    datasets: str = Field(
        ..., description="Dataset or data sources used, or 'Not specified in the available abstract.'"
    )
    key_findings: List[str] = Field(
        default_factory=list, description="Key results and contributions of the paper"
    )
    limitations: str = Field(
        ..., description="Limitations or constraints, or 'Not specified in the available abstract.'"
    )
    future_work: str = Field(
        ..., description="Suggested future directions, or 'Not specified in the available abstract.'"
    )

    @field_validator("key_findings", mode="before")
    @classmethod
    def normalize_key_findings(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return []

    @field_validator("datasets", "limitations", "future_work", "methodology", "research_problem", mode="before")
    @classmethod
    def normalize_strings(cls, v: Union[str, List[str], None]) -> str:
        if v is None:
            return "Not specified in the available abstract."
        if isinstance(v, list):
            return "; ".join(str(item).strip() for item in v if str(item).strip())
        return str(v).strip()
