# backend/agents/analysis.py

"""Paper Analysis Agent (Phase 4).

Analyzes discovered research papers using Groq LLM based strictly
on available titles, abstracts, and metadata.
"""

import os
import json
import requests
import time
from typing import Dict, Any, List, Optional

import backend.config  # ensures .env is loaded
from backend.schemas.analysis import PaperAnalysis

# RAG imports
from backend.rag.loader import get_paper_content
from backend.rag.chunker import chunk_text
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever


def _call_groq_analysis(model: str, api_key: str, paper: Dict[str, Any], evidence_chunks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Send paper analysis prompt to Groq using retrieved evidence chunks.

    Returns the parsed JSON dictionary, or None if the call fails or cannot be parsed.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an expert scientific research analyst. Your task is to analyze the provided research paper "
        "based strictly and ONLY on the retrieved evidence provided.\n\n"
        "STRICT EVIDENCE RULES:\n"
        "1. Answer ONLY from the supplied retrieved evidence.\n"
        "2. Do NOT hallucinate, invent, or speculate on datasets, methodologies, findings, or limitations. Do not use your background knowledge.\n"
        "3. If the evidence does not contain the information for a field, you MUST set that field to: "
        "'Not specified in the available evidence.'\n"
        "4. Return ONLY valid JSON matching this schema with no additional commentary or markdown code fences:\n"
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
    authors = paper.get("authors") or []
    authors_str = ", ".join(authors[:5]) if authors else "Unknown"

    evidence_text = "\n\n".join([f"Evidence Chunk {i+1}:\n{chunk['text']}" for i, chunk in enumerate(evidence_chunks)])
    if not evidence_text:
        evidence_text = "No evidence available."

    user_prompt = (
        f"Paper ID: {paper_id}\n"
        f"Title: {title}\n"
        f"Authors: {authors_str}\n\n"
        f"--- RETRIEVED EVIDENCE ---\n{evidence_text}\n--------------------------\n\n"
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

    for attempt in range(4):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 429:
                sleep_time = 3 * (attempt + 1)
                print(f"[Analysis] Groq 429 rate limit hit for '{title}'. Retrying in {sleep_time}s...")
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

            if not parsed.get("paper_id"):
                parsed["paper_id"] = paper_id
            if not parsed.get("title"):
                parsed["title"] = title

            # Attach evidence sources
            parsed["evidence_sources"] = evidence_chunks

            return parsed
        except Exception as e:
            if attempt == 3:
                print(f"[Analysis] Groq analysis error for paper '{title}': {e}")
                return None
            time.sleep(2)


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
    """Analysis node – analyzes papers from state['papers'] using RAG and Groq."""
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

    # Initialize RAG components (do this once per run to save model load time, though loading each time is slow)
    vector_store = VectorStore()
    retriever = Retriever(vector_store)

    for i, paper in enumerate(papers[:5]): # Process up to 5 papers to avoid rate limits/time limits in demo
        if i > 0:
            time.sleep(0.5)
            
        # 1. Obtain available content
        text_content = get_paper_content(paper)
        
        # 2. Add/chunk/index it in the vector store
        # We index per-paper or per-batch, but since we analyze per paper, we can just index it
        # Actually, if we index all papers first, we could retrieve from all, but the Analysis Agent
        # analyzes EACH paper individually. Let's index just this paper's chunks in a fresh VectorStore
        # OR we index all papers once and retrieve with a paper_id filter.
        # FAISS doesn't easily support metadata filtering out-of-the-box in the simple wrapper, 
        # so we will use a fresh vector store for each paper to ensure evidence is from *this* paper,
        # OR we could just let it retrieve from any paper, but the analysis is for a specific paper.
        # It's better to index just this paper's content for its specific analysis, or just trust the LLM.
        # Let's index just this paper for speed and accuracy of single-paper analysis.
        
        vector_store.clear()
        chunks = chunk_text(text_content, paper)
        vector_store.add_chunks(chunks)
        local_retriever = Retriever(vector_store)
        
        # 3. Generate relevant analysis queries
        query = "What is the core research problem, methodology, datasets used, key findings, limitations, and future work?"
        
        # 4. Retrieve relevant chunks
        evidence_chunks = local_retriever.retrieve_relevant_evidence(query, k=5)

        # 5. Send the retrieved evidence to Groq
        parsed_dict = _call_groq_analysis(model, api_key, paper, evidence_chunks)

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
                # 6. Validate using the existing Pydantic schema
                validated = PaperAnalysis(**parsed_dict)
                analysis_results.append(validated.model_dump())
            except Exception as val_err:
                print(f"[Analysis] Validation error for paper '{paper.get('title')}': {val_err}. Using fallback.")
                fallback = _create_fallback_analysis(paper, reason="Validation failed")
                analysis_results.append(fallback)

    state["analysis_results"] = analysis_results
    return state
