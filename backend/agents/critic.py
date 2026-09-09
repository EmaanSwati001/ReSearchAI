# backend/agents/critic.py

"""Placeholder Research Critic Agent.
Currently returns the state unchanged.
"""

from typing import Dict, Any

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Critic node – later will evaluate gaps.
    For now, just passes the state through.
    """
    return state
