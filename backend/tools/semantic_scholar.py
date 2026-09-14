# backend/tools/semantic_scholar.py

"""Semantic Scholar API wrapper for paper discovery (Phase 3).

Uses the Semantic Scholar Academic Graph API to search for papers.
API docs: https://api.semanticscholar.org/

The API key is optional — it works without one but is rate-limited.
"""

import os
import requests
from typing import List

from backend.schemas.paper import Paper

# API configuration
SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,authors,abstract,year,paperId,url,citationCount,venue,externalIds"


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    """Search Semantic Scholar for papers matching the query.

    Args:
        query: Search string (e.g. "machine learning medical diagnosis").
        limit: Maximum number of papers to return.

    Returns:
        List of Paper objects. Returns empty list if the API fails.
    """
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": query,
        "limit": limit,
        "fields": FIELDS,
    }

    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=8)
        # If API key returned 429 or 403, retry without API key
        if response.status_code in (429, 403) and "x-api-key" in headers:
            print(f"[Semantic Scholar] API key returned {response.status_code}. Retrying without API key...")
            headers.pop("x-api-key")
            response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=8)
        
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Semantic Scholar] API request failed: {e}")
        raise

    raw_papers = data.get("data", [])
    papers: List[Paper] = []

    for item in raw_papers:
        # Extract author names from the nested author objects
        authors = []
        for author in (item.get("authors") or []):
            name = author.get("name")
            if name:
                authors.append(name)

        paper = Paper(
            title=item.get("title", "Untitled"),
            authors=authors,
            abstract=item.get("abstract"),
            year=item.get("year"),
            source="semantic_scholar",
            paper_id=item.get("paperId"),
            url=item.get("url"),
            citation_count=item.get("citationCount"),
            venue=item.get("venue") or None,
        )
        papers.append(paper)

    return papers
