# backend/agents/discovery.py

"""Paper Discovery Agent (Phase 3).

This agent reads the Planner's output from the LangGraph state,
builds search queries, and searches Semantic Scholar and arXiv
for relevant research papers.
"""

from typing import Dict, Any, List

from backend.schemas.paper import Paper
from backend.tools import semantic_scholar, arxiv


def _extract_search_query(planner_output: Dict[str, Any]) -> str:
    """Build a simple search query string from the Planner's output.

    Combines keywords and the plan title into a single query string
    suitable for Semantic Scholar's free-text search.
    """
    keywords = planner_output.get("keywords", [])
    title = planner_output.get("title", "")

    # Use keywords if available, otherwise fall back to the plan title
    if keywords:
        return " ".join(keywords)
    return title


def _extract_arxiv_keywords(planner_output: Dict[str, Any]) -> List[str]:
    """Extract keywords for arXiv's structured query format.

    Returns a list of keyword strings. Falls back to subtopics or
    the plan title if no keywords are available.
    """
    keywords = planner_output.get("keywords", [])
    if keywords:
        return keywords[:5]  # Limit to avoid overly restrictive queries

    subtopics = planner_output.get("subtopics", [])
    if subtopics:
        return subtopics[:3]

    title = planner_output.get("title", "")
    if title:
        return [title]

    return []


def _deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """Remove duplicate papers based on paper_id or normalized title.

    Priority:
    1. If two papers share the same paper_id (and it's not None), keep the first.
    2. If two papers have the same normalized title, keep the first.
    """
    seen_ids: set = set()
    seen_titles: set = set()
    unique_papers: List[Paper] = []

    for paper in papers:
        # Check by paper_id first
        if paper.paper_id:
            if paper.paper_id in seen_ids:
                continue
            seen_ids.add(paper.paper_id)

        # Check by normalized title
        normalized_title = paper.title.strip().lower()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)

        unique_papers.append(paper)

    return unique_papers


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Discovery node — searches Semantic Scholar and arXiv for papers.

    Reads the Planner output from state["planner_output"], builds search
    queries, calls both APIs, deduplicates results, and stores them
    in state["papers"].
    """
    planner_output = state.get("planner_output")

    if not planner_output:
        # No planner output available — nothing to search for
        state["papers"] = []
        return state

    # Build search queries from the planner's output
    ss_query = _extract_search_query(planner_output)
    arxiv_keywords = _extract_arxiv_keywords(planner_output)
    arxiv_query = arxiv._build_query(arxiv_keywords) if arxiv_keywords else ""

    all_papers: List[Paper] = []
    errors: List[str] = []

    # --- Semantic Scholar ---
    if ss_query:
        try:
            ss_papers = semantic_scholar.search_papers(ss_query, limit=10)
            all_papers.extend(ss_papers)
            print(f"[Discovery] Semantic Scholar returned {len(ss_papers)} papers")
        except Exception as e:
            errors.append(f"Semantic Scholar failed: {e}")
            print(f"[Discovery] Semantic Scholar error: {e}")

    # --- arXiv ---
    if arxiv_query:
        try:
            arxiv_papers = arxiv.search_papers(arxiv_query, limit=10)
            all_papers.extend(arxiv_papers)
            print(f"[Discovery] arXiv returned {len(arxiv_papers)} papers")
        except Exception as e:
            errors.append(f"arXiv failed: {e}")
            print(f"[Discovery] arXiv error: {e}")

    # Deduplicate
    unique_papers = _deduplicate_papers(all_papers)
    print(f"[Discovery] {len(unique_papers)} unique papers after deduplication")

    # Store as list of dicts (compatible with LangGraph state)
    state["papers"] = [paper.model_dump() for paper in unique_papers]

    # Append any errors to the state (don't overwrite existing errors)
    if errors:
        existing_errors = state.get("errors") or []
        state["errors"] = existing_errors + errors

    return state
