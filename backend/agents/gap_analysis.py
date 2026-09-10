# backend/agents/gap_analysis.py

"""Gap Analysis Agent (Phase 5).

Compares analyzed research papers to identify cross-paper research gaps,
repeated limitations, methodology/evaluation gaps, contradictions,
and future research opportunities based strictly on evidence.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional

import backend.config  # ensures .env is loaded
from backend.schemas.gap import ResearchGap


def _call_groq_gap_analysis(model: str, api_key: str, compact_papers: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """Send cross-paper comparison prompt to Groq.

    Returns the parsed list of gap dictionaries, or None if the call fails or cannot be parsed.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an expert scientific meta-analyst. Your task is to compare a provided set of analyzed "
        "research papers and identify genuine cross-paper research gaps, repeated limitations, "
        "methodology/evaluation gaps, contradictions, or convergent future directions.\n\n"
        "STRICT SCIENTIFIC EVIDENCE RULES:\n"
        "1. Reason ONLY from the provided paper titles, problems, methodologies, datasets, findings, limitations, and future work.\n"
        "2. Do NOT claim that something is a research gap merely because it was not mentioned in the provided papers.\n"
        "3. Only identify a gap when there is explicit evidence across the papers (e.g. multiple papers noting the same limitation, "
        "an underexplored method/dataset within this sample, conflicting findings between papers, or converging future work suggestions).\n"
        "4. Distinguish evidence from hypothesis. If the evidence is preliminary or thin, set confidence to 'Low'.\n"
        "5. Use cautious, objective scientific language (e.g. 'Within the supplied papers...', 'The reviewed papers suggest...', "
        "'An underexplored area in this sample is...'). Avoid sweeping claims like 'No research exists on...'.\n"
        "6. Return ONLY valid JSON with no commentary or markdown code fences, strictly matching this structure:\n"
        "{\n"
        '  "gaps": [\n'
        "    {\n"
        '      "gap": "Concise cautious description of the gap",\n'
        '      "evidence": "Specific evidence from the papers that supports this gap",\n'
        '      "supporting_papers": ["Paper ID or title 1", "Paper ID or title 2"],\n'
        '      "gap_type": "Dataset Gap | Methodology Gap | Evaluation Gap | Application Gap | Contradiction | Limitation Gap",\n'
        '      "confidence": "High | Medium | Low",\n'
        '      "research_opportunity": "Concrete investigative question or direction for future research"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    # Format compact representation
    papers_context = []
    for i, p in enumerate(compact_papers, 1):
        pid = p.get("paper_id") or f"P{i}"
        title = p.get("title", f"Paper {i}")
        problem = p.get("research_problem", "N/A")
        method = p.get("methodology", "N/A")
        datasets = p.get("datasets", "N/A")
        findings = p.get("key_findings", [])
        findings_str = "; ".join(findings) if isinstance(findings, list) else str(findings)
        limitations = p.get("limitations", "N/A")
        future_work = p.get("future_work", "N/A")

        papers_context.append(
            f"Paper [{pid}]: {title}\n"
            f"  - Research Problem: {problem}\n"
            f"  - Methodology: {method}\n"
            f"  - Datasets: {datasets}\n"
            f"  - Key Findings: {findings_str}\n"
            f"  - Stated Limitations: {limitations}\n"
            f"  - Suggested Future Work: {future_work}"
        )

    user_prompt = (
        f"Below are {len(compact_papers)} analyzed papers from the research literature sample:\n\n"
        + "\n\n".join(papers_context)
        + "\n\nCompare these papers and identify all justified research gaps following the strict scientific evidence rules. Return pure JSON."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
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
        if isinstance(parsed, dict) and "gaps" in parsed:
            return parsed["gaps"]
        if isinstance(parsed, list):
            return parsed
        return None
    except Exception as e:
        print(f"[GapAnalysis] Groq gap analysis error: {e}")
        return None


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Gap Analysis node – cross-compares analyzed papers to identify research gaps."""
    analysis_results = state.get("analysis_results") or []
    papers = state.get("papers") or []

    # If fewer than 2 usable papers, return empty gaps without fabricating cross-paper claims
    if len(analysis_results) < 2 and len(papers) < 2:
        state["gaps"] = []
        state["research_gaps"] = []
        return state

    # Combine analysis results and paper metadata for compact context
    compact_papers: List[Dict[str, Any]] = []

    if analysis_results:
        # Use structured analysis results (limit up to 8 papers to respect token limits)
        compact_papers = analysis_results[:8]
    else:
        # Fallback to raw papers if analysis_results is empty
        for p in papers[:8]:
            compact_papers.append({
                "paper_id": p.get("paper_id"),
                "title": p.get("title"),
                "research_problem": p.get("abstract", "")[:200],
                "methodology": "Not specified in the available abstract.",
                "datasets": "Not specified in the available abstract.",
                "key_findings": [p.get("abstract", "")[:200]] if p.get("abstract") else [],
                "limitations": "Not specified in the available abstract.",
                "future_work": "Not specified in the available abstract.",
            })

    if len(compact_papers) < 2:
        state["gaps"] = []
        state["research_gaps"] = []
        return state

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    if not api_key:
        # Graceful fallback without crashing
        state["gaps"] = []
        state["research_gaps"] = []
        return state

    raw_gaps = _call_groq_gap_analysis(model, api_key, compact_papers)

    validated_gaps: List[Dict[str, Any]] = []
    if raw_gaps:
        for g in raw_gaps:
            try:
                model_gap = ResearchGap(**g)
                validated_gaps.append(model_gap.model_dump())
            except Exception as err:
                print(f"[GapAnalysis] Gap validation warning: {err}")

    state["gaps"] = validated_gaps
    state["research_gaps"] = validated_gaps
    return state
