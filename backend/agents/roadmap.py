# backend/agents/roadmap.py

"""Research Roadmap Agent (Phase 8).

Generates an actionable research plan based on the evaluated gaps.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

import backend.config
from backend.schemas.roadmap import RoadmapResult

def _call_groq_roadmap(model: str, api_key: str, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send roadmap generation prompt to Groq."""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    system_prompt = (
        "You are an experienced academic research mentor.\n"
        "Your task is to convert evaluated research gaps into a practical research roadmap for a student or early-stage researcher.\n\n"
        "STRICT EVALUATION RULES:\n"
        "1. Prioritize research gaps that have stronger supporting evidence (Supported + High/Medium Evidence).\n"
        "2. Do not treat weak or insufficiently supported gaps as established facts. If only weak gaps are provided, the roadmap must center around further literature validation.\n"
        "3. If a gap is partially supported, include validation steps before full implementation.\n"
        "4. The roadmap should be practical, specific, measurable, and realistic.\n"
        "5. Separate what is supported by the provided evidence from what is a proposed research plan (do not invent facts).\n"
        "6. Return ONLY valid JSON with exactly these fields:\n"
        "{\n"
        '  "research_direction": "string",\n'
        '  "objective": "string",\n'
        '  "research_questions": ["string"],\n'
        '  "methodology": ["string"],\n'
        '  "data_requirements": ["string"],\n'
        '  "implementation_steps": ["string"],\n'
        '  "evaluation_metrics": ["string"],\n'
        '  "expected_challenges": ["string"],\n'
        '  "expected_outcomes": ["string"],\n'
        '  "validation_steps": ["string"],\n'
        '  "timeline_weeks": 8\n'
        "}\n"
        "Do not add additional JSON fields."
    )
    
    # Format the context safely
    context_text = f"USER TOPIC: {state.get('user_topic', 'Unknown')}\n"
    
    planner = state.get("planner_output", {})
    if planner:
        context_text += f"\nPLANNER OBJECTIVE: {planner.get('objective', 'N/A')}\n"
        
    gaps = state.get("gaps", [])
    critic_results = state.get("critic_results", [])
    
    context_text += "\n--- EVALUATED RESEARCH GAPS ---\n"
    if gaps and critic_results and len(gaps) == len(critic_results):
        for idx, (gap, critic) in enumerate(zip(gaps, critic_results)):
            context_text += f"\nGAP {idx+1}:\n"
            context_text += f"Gap Text: {gap.get('gap', 'N/A')}\n"
            context_text += f"Verdict: {critic.get('verdict', 'Unknown')}\n"
            context_text += f"Evidence Strength: {critic.get('evidence_strength', 'Unknown')}\n"
            context_text += f"Critic Reasoning: {critic.get('reasoning', 'N/A')}\n"
            context_text += f"Critic Recommendation: {critic.get('recommendation', 'N/A')}\n"
    else:
        context_text += "No valid gaps or critic results available.\n"
        
    user_prompt = (
        f"{context_text}\n\n"
        "Based on the above context and critic evaluations, generate the research roadmap JSON."
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
    
    import time
    for attempt in range(4):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 429:
                sleep_time = 3 * (attempt + 1)
                print(f"[Roadmap] Groq 429 rate limit hit. Retrying in {sleep_time}s...")
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
            return parsed
        except Exception as e:
            if attempt == 3:
                print(f"[Roadmap] Groq roadmap error: {e}")
                return None
            time.sleep(2)

def _create_fallback_roadmap(state: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """Create a fallback roadmap grounded in the user's topic when data is missing."""
    topic = state.get("user_topic", "Research Topic")
    planner = state.get("planner_output", {})
    title = planner.get("title", f"Research Plan: {topic}")
    keywords = planner.get("keywords", [topic])
    kw_str = ", ".join(keywords[:3]) if keywords else topic

    return {
        "research_direction": f"Empirical Evaluation & Methodological Advances in {topic}",
        "objective": f"Address core computational and generalization limitations in {kw_str}.",
        "research_questions": [
            f"How do current state-of-the-art models perform under real-world domain shifts in {topic}?",
            f"What specific architectural or data enhancements resolve current performance bottlenecks in {kw_str}?"
        ],
        "methodology": [
            f"Systematic literature evaluation of {topic} benchmarks.",
            "Ablation studies on core model components and dataset variations."
        ],
        "data_requirements": [
            f"Standard open academic datasets for {topic}.",
            "Custom validation subsets for robust evaluation."
        ],
        "implementation_steps": [
            f"1. Establish baseline model environment for {topic}.",
            "2. Implement proposed architectural modifications and training pipeline.",
            "3. Conduct comprehensive cross-dataset evaluation and ablation analysis."
        ],
        "evaluation_metrics": ["Accuracy/F1-Score", "Generalization Latency", "Ablation Accuracy Delta"],
        "expected_challenges": [f"Data heterogeneity and computational requirements for {topic}."],
        "expected_outcomes": [f"Novel methodological framework improving state-of-the-art performance in {topic}."],
        "validation_steps": ["Cross-validation across diverse datasets", "Statistical significance testing"],
        "timeline_weeks": 6
    }

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Roadmap node – generates a final actionable research plan."""
    
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    
    # Validation checks
    if not api_key:
        fallback = _create_fallback_roadmap(state, "GROQ_API_KEY missing")
        try:
            validated = RoadmapResult(**fallback)
            state["roadmap"] = validated.model_dump()
        except Exception:
            state["roadmap"] = fallback
        return state
        
    gaps = state.get("gaps", [])
    critic_results = state.get("critic_results", [])
    
    parsed_dict = _call_groq_roadmap(model, api_key, state)
    
    if parsed_dict is None:
        fallback = _create_fallback_roadmap(state, "Groq request failed or missing gaps")
        try:
            validated = RoadmapResult(**fallback)
            state["roadmap"] = validated.model_dump()
        except Exception:
            state["roadmap"] = fallback
    else:
        try:
            validated = RoadmapResult(**parsed_dict)
            state["roadmap"] = validated.model_dump()
        except Exception as val_err:
            print(f"[Roadmap] Validation error: {val_err}. Using fallback.")
            fallback = _create_fallback_roadmap("Validation failed")
            state["roadmap"] = fallback
            
    return state
