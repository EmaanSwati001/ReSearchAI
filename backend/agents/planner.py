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
        "max_tokens": 1000,
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Extract the assistant message content
        content = data["choices"][0]["message"]["content"]
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"[Planner] Groq API call error: {e}")
        return None


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Planner node – generates a structured research plan using Groq.

    Expected ``state`` keys:
    - ``user_topic`` (str): broad research topic supplied by the user
    - ``experience_level`` (str): user's experience level
    - ``user_interest`` (Optional[str]): optional specific area of interest
    """
    import backend.config  # ensure .env is loaded
    # Load configuration from environment
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    if not api_key:
        # If the key is missing we generate a fallback plan using user inputs
        topic = state.get("user_topic", "Research Topic")
        interest = state.get("user_interest")
        keywords = [t.strip() for t in [topic, interest] if t and t.strip().lower() not in ("none", "")]
        plan_dict = {
            "title": f"Research Plan: {topic}",
            "summary": f"A structured research plan for {topic}.",
            "keywords": keywords if keywords else [topic],
            "subtopics": [f"Foundations of {topic}", f"Applications of {topic}"],
            "research_questions": [f"What are current key advancements and methodologies in {topic}?"],
            "methodology_suggestions": ["Literature Review", "Empirical Evaluation"],
            "timeline_weeks": 4,
        }
        state["planner_output"] = plan_dict
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
        # Fallback with real keywords based on topic so downstream discovery works
        topic = state.get("user_topic", "Research Topic")
        interest = state.get("user_interest")
        keywords = [t.strip() for t in [topic, interest] if t and t.strip().lower() not in ("none", "")]
        plan_dict = {
            "title": f"Research Plan: {topic}",
            "summary": f"A structured research plan covering {topic}.",
            "keywords": keywords if keywords else [topic],
            "subtopics": [f"Foundations of {topic}", f"Applications of {topic}"],
            "research_questions": [f"What are current key advancements and methodologies in {topic}?"],
            "methodology_suggestions": ["Literature Review", "Empirical Evaluation"],
            "timeline_weeks": 4,
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

