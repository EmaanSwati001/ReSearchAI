# backend/agents/critic.py

"""Research Critic Agent (Phase 7).

Evaluates the proposed research gaps against the available evidence.
"""

import os
import json
import requests
import time
from typing import Dict, Any, List, Optional

import backend.config
from backend.schemas.critic import CriticResult


def _call_groq_critic(model: str, api_key: str, gap: Dict[str, Any], analysis_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Send gap evaluation prompt to Groq.

    Returns the parsed JSON dictionary, or None if the call fails.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are a critical research mentor. Your job is to evaluate whether a proposed research gap is actually "
        "supported by the supplied evidence.\n\n"
        "STRICT EVALUATION RULES:\n"
        "1. Do not accept the proposed gap automatically.\n"
        "2. Evaluate whether the supplied evidence actually supports it.\n"
        "3. If evidence is insufficient, say so.\n"
        "4. Do not make claims about the entire scientific literature. Only judge based on the provided papers.\n"
        "5. Return ONLY valid JSON matching this schema:\n"
        "{\n"
        '  "gap": string,\n'
        '  "verdict": "Supported" | "Partially Supported" | "Weak / Needs More Evidence",\n'
        '  "evidence_strength": "High" | "Medium" | "Low",\n'
        '  "reasoning": string,\n'
        '  "concerns": string,\n'
        '  "recommendation": string\n'
        "}"
    )

    # Format the evidence safely
    evidence_text = ""
    for idx, analysis in enumerate(analysis_results):
        title = analysis.get("title", f"Paper {idx+1}")
        problem = analysis.get("research_problem", "N/A")
        limitations = analysis.get("limitations", "N/A")
        findings = analysis.get("key_findings", [])
        
        # Include RAG evidence sources if available
        rag_evidence = analysis.get("evidence_sources", [])
        rag_text = ""
        if rag_evidence:
            rag_text = "\n  RAG Evidence Snippets:\n"
            for chunk in rag_evidence:
                rag_text += f"    - {chunk.get('text', '')}\n"
        
        evidence_text += (
            f"Paper: {title}\n"
            f"  Problem: {problem}\n"
            f"  Limitations: {limitations}\n"
            f"  Findings: {findings}\n"
            f"{rag_text}\n"
        )

    user_prompt = (
        f"RESEARCH GAP PROPOSED:\n{gap.get('gap', 'Unknown Gap')}\n\n"
        f"GAP TYPE:\n{gap.get('gap_type', 'Unknown Type')}\n\n"
        f"PROPOSED EVIDENCE:\n{gap.get('evidence', 'No evidence provided')}\n\n"
        f"--- AVAILABLE PAPER EVIDENCE ---\n{evidence_text}\n--------------------------\n\n"
        "Critically evaluate this gap based strictly on the available paper evidence. Return pure JSON."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1000,
    }

    for attempt in range(4):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 429:
                sleep_time = 3 * (attempt + 1)
                print(f"[Critic] Groq 429 rate limit hit. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
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
            
            # Ensure the gap text is preserved if the LLM hallucinated it
            if not parsed.get("gap") or parsed.get("gap") == "string":
                parsed["gap"] = gap.get("gap", "Unknown Gap")
                
            return parsed
        except Exception as e:
            if attempt == 3:
                print(f"[Critic] Groq critic error: {e}")
                return None
            time.sleep(2)

def _create_fallback_critic(gap: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """Create a fallback critic result when API fails."""
    return {
        "gap": gap.get("gap", "Unknown Gap"),
        "verdict": "Weak / Needs More Evidence",
        "evidence_strength": "Low",
        "reasoning": f"Critic evaluation unavailable ({reason}).",
        "concerns": "Cannot verify gap validity due to system error.",
        "recommendation": "Review the gap manually.",
    }

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Critic node – evaluates proposed research gaps."""
    gaps = state.get("gaps", [])
    analysis_results = state.get("analysis_results", [])
    
    if not gaps:
        state["critic_results"] = []
        return state

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    critic_results: List[Dict[str, Any]] = []

    if not api_key:
        for gap in gaps:
            fallback = _create_fallback_critic(gap, "GROQ_API_KEY missing")
            try:
                validated = CriticResult(**fallback)
                critic_results.append(validated.model_dump())
            except Exception:
                critic_results.append(fallback)
        state["critic_results"] = critic_results
        return state

    for i, gap in enumerate(gaps):
        if i > 0:
            time.sleep(0.5)
            
        parsed_dict = _call_groq_critic(model, api_key, gap, analysis_results)
        
        if parsed_dict is None:
            fallback = _create_fallback_critic(gap, "Groq request failed")
            try:
                validated = CriticResult(**fallback)
                critic_results.append(validated.model_dump())
            except Exception:
                critic_results.append(fallback)
        else:
            try:
                validated = CriticResult(**parsed_dict)
                critic_results.append(validated.model_dump())
            except Exception as val_err:
                print(f"[Critic] Validation error: {val_err}. Using fallback.")
                fallback = _create_fallback_critic(gap, "Validation failed")
                critic_results.append(fallback)

    state["critic_results"] = critic_results
    return state
