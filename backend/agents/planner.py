# backend/agents/planner.py
"""Research Planner Agent (Phase 2).

This agent calls the Groq LLM to generate a structured research plan.
The result is stored in the LangGraph state under the key
`planner_output` as a plain ``dict`` (compatible with the
``PlannerOutput`` Pydantic model).
"""

import os
import json
import requests
from typing import Dict, Any, Optional

from backend.schemas.planner import PlannerOutput


def _call_groq(model: str, api_key: str, messages: list) -> Optional[Dict[str, Any]]:
    """Send a chat completion request to Groq.

    Returns the parsed JSON content from the assistant's first message,
    or ``None`` if the request fails or the content cannot be parsed.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Extract the assistant message content
        content = data["choices"][0]["message"]["content"]
        # The LLM is instructed to output pure JSON, so we parse it.
        return json.loads(content)
    except Exception as e:
        # In a production system you would log the error.
        return None


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Planner node – generates a structured research plan using Groq.

    Expected ``state`` keys:
    - ``user_topic`` (str): broad research topic supplied by the user
    - ``experience_level`` (str): user's experience level
    - ``user_interest`` (Optional[str]): optional specific area of interest
    """
    # Load configuration from environment
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    if not api_key:
        # If the key is missing we simply return the state unchanged.
        return state

    # Build the prompt – we ask the model to return JSON matching PlannerOutput.
    system_msg = {
        "role": "system",
        "content": (
            "You are a research mentor. Generate a concise research plan based on the "
            "user's topic, experience level, and optional specific interest. Return the "
            "plan as **pure JSON** that conforms to the following schema: "
            "{\"title\": str, \"summary\": str, \"keywords\": [str], \"subtopics\": [str], "
            "\"research_questions\": [str], \"methodology_suggestions\": [str], "
            "\"timeline_weeks\": int or null}."
        ),
    }
    user_msg = {
        "role": "user",
        "content": (
            f"Topic: {state.get('user_topic', '')}\n"
            f"Experience level: {state.get('experience_level', '')}\n"
            f"Specific interest: {state.get('user_interest', '')}\n"
        ),
    }
    messages = [system_msg, user_msg]

    plan_dict: Optional[Dict[str, Any]] = _call_groq(model, api_key, messages)

    if plan_dict is None:
        # Fallback – static placeholder plan so downstream nodes keep working.
        plan_dict = {
            "title": "Research Plan (fallback)",
            "summary": "A generic plan generated because the LLM call failed.",
            "keywords": [],
            "subtopics": [],
            "research_questions": [],
            "methodology_suggestions": [],
            "timeline_weeks": None,
        }

    # Validate against the Pydantic model (will raise if incompatible).
    try:
        PlannerOutput(**plan_dict)
    except Exception:
        # If validation fails we still store the raw dict.
        pass

    # Attach to the LangGraph state.
    state["planner_output"] = plan_dict
    return state

