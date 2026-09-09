# backend/agents/analysis.py

"""Placeholder Paper Analysis Agent.
Currently returns the state unchanged.
"""

from typing import Dict, Any

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis node – later will extract information from papers.
    For now, just passes the state through.
    """
    return state
