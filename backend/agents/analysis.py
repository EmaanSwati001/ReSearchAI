# backend/agents/analysis.py

"""Paper Analysis Agent (Phase 4).

Analyzes discovered research papers using Groq LLM based strictly
on available titles, abstracts, and metadata.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional

import backend.config  # ensures .env is loaded
from backend.schemas.analysis import PaperAnalysis


def _call_groq_analysis(model: str, api_key: str, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send paper analysis prompt to Groq.

    Returns the parsed JSON dictionary, or None if the call fails or cannot be parsed.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an expert scientific research analyst. Your task is to analyze the provided research paper "
        "based strictly and only on the information provided in its title, abstract, and metadata.\n\n"
        "STRICT EVIDENCE RULES:\n"
        "1. Only use factual information directly supported by the supplied text.\n"
        "2. Do NOT hallucinate, invent, or speculate on datasets, methodologies, findings, or limitations.\n"
        "3. If the abstract does not explicitly state or provide enough information for a field, you MUST set that field to: "
        "'Not specified in the available abstract.'\n"
        "4. Clearly distinguish what is stated in the paper from what cannot be determined.\n"
        "5. Return ONLY valid JSON matching this schema with no additional commentary or markdown code fences:\n"
        "{\n"
        '  "paper_id": string or null,\n'
        '  "title": string,\n'
        '  "research_problem": string,\n'
        '  "methodology": string,\n'
        '  "datasets": string,\n'
        '  "key_findings": [string],\n'
        '  "limitations": string,\n'
        '  "future_work": string\n'
        "}"
    )

    paper_id = paper.get("paper_id")
    title = paper.get("title", "Untitled")
    abstract = paper.get("abstract") or "No abstract available."
    year = paper.get("year")
    authors = paper.get("authors") or []
    authors_str = ", ".join(authors[:5]) if authors else "Unknown"

    user_prompt = (
        f"Paper ID: {paper_id}\n"
        f"Title: {title}\n"
        f"Authors: {authors_str}\n"
        f"Year: {year}\n\n"
        f"Abstract:\n{abstract}\n\n"
        "Analyze this paper adhering strictly to the evidence rules. Return pure JSON."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        parsed = json.loads(cleaned)

        if not parsed.get("paper_id"):
            parsed["paper_id"] = paper_id
        if not parsed.get("title"):
            parsed["title"] = title

        return parsed
    except Exception as e:
        print(f"[Analysis] Groq analysis error for paper '{title}': {e}")
        return None


def _create_fallback_analysis(paper: Dict[str, Any], reason: str = "LLM analysis unavailable") -> Dict[str, Any]:
    """Create a factual fallback analysis when LLM is unavailable or fails."""
    abstract = paper.get("abstract") or ""
    summary_preview = (abstract[:250] + "...") if len(abstract) > 250 else abstract

    return {
        "paper_id": paper.get("paper_id"),
        "title": paper.get("title", "Untitled"),
        "research_problem": summary_preview if summary_preview else "Not specified in the available abstract.",
        "methodology": "Not specified in the available abstract.",
        "datasets": "Not specified in the available abstract.",
        "key_findings": [f"Analysis fallback ({reason}). Refer to abstract."],
        "limitations": "Not specified in the available abstract.",
        "future_work": "Not specified in the available abstract.",
    }


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis node – analyzes papers from state['papers'] using Groq."""
    papers = state.get("papers")

    if not papers:
        state["analysis_results"] = []
        return state

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    analysis_results: List[Dict[str, Any]] = []

    # If no API key is set, produce fallback analyses without crashing
    if not api_key:
        for paper in papers:
            fallback = _create_fallback_analysis(paper, reason="GROQ_API_KEY missing")
            try:
                validated = PaperAnalysis(**fallback)
                analysis_results.append(validated.model_dump())
            except Exception:
                analysis_results.append(fallback)
        state["analysis_results"] = analysis_results
        return state

    import time
    for i, paper in enumerate(papers[:5]):
        if i > 0:
            time.sleep(0.5)
        parsed_dict = _call_groq_analysis(model, api_key, paper)

        if parsed_dict is None:
            # Fallback for this single paper so remaining papers continue
            fallback = _create_fallback_analysis(paper, reason="Groq request failed")
            try:
                validated = PaperAnalysis(**fallback)
                analysis_results.append(validated.model_dump())
            except Exception:
                analysis_results.append(fallback)
        else:
            try:
                validated = PaperAnalysis(**parsed_dict)
                analysis_results.append(validated.model_dump())
            except Exception as val_err:
                print(f"[Analysis] Validation error for paper '{paper.get('title')}': {val_err}. Using fallback.")
                fallback = _create_fallback_analysis(paper, reason="Validation failed")
                analysis_results.append(fallback)

    state["analysis_results"] = analysis_results
    return state
