# backend/schemas/paper.py

"""Pydantic model for a discovered research paper (Phase 3)."""

from pydantic import BaseModel, Field
from typing import Optional, List


class Paper(BaseModel):
    """A single research paper discovered from Semantic Scholar or arXiv."""

    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    abstract: Optional[str] = Field(None, description="Paper abstract or summary")
    year: Optional[int] = Field(None, description="Publication year")
    source: str = Field(..., description="Where the paper was found: 'semantic_scholar' or 'arxiv'")
    paper_id: Optional[str] = Field(None, description="Source-specific paper ID")
    url: Optional[str] = Field(None, description="Link to the paper")
    citation_count: Optional[int] = Field(None, description="Number of citations (Semantic Scholar only)")
    venue: Optional[str] = Field(None, description="Conference or journal name")
