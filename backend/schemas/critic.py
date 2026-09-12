# backend/schemas/critic.py

"""Pydantic schema for the Research Critic Agent (Phase 7).

Represents the critical evaluation of a single research gap.
"""

from typing import Literal
from pydantic import BaseModel, Field

class CriticResult(BaseModel):
    """Evaluation of a proposed research gap."""

    gap: str = Field(..., description="The research gap being evaluated.")
    verdict: Literal["Supported", "Partially Supported", "Weak / Needs More Evidence"] = Field(
        ..., description="The overall verdict on the validity of the gap."
    )
    evidence_strength: Literal["High", "Medium", "Low"] = Field(
        ..., description="Strength of the available evidence."
    )
    reasoning: str = Field(
        ..., description="Explanation of why this verdict was reached based strictly on the provided evidence."
    )
    concerns: str = Field(
        ..., description="Potential weaknesses, limitations, or caveats regarding this gap."
    )
    recommendation: str = Field(
        ..., description="Recommended next steps for the researcher to validate or explore this gap."
    )
