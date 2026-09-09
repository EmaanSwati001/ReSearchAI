# backend/tools/arxiv.py

"""arXiv API wrapper for paper discovery (Phase 3).

Uses the arXiv Atom API to search for papers.
API docs: https://info.arxiv.org/help/api/

No API key is required.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List

from backend.schemas.paper import Paper

# API configuration
SEARCH_URL = "http://export.arxiv.org/api/query"

# Atom XML namespace used by arXiv
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _build_query(keywords: List[str]) -> str:
    """Build an arXiv search query from a list of keywords.

    Joins keywords with AND so that results match all terms.
    Example: ["machine learning", "medical"] -> 'all:"machine learning"+AND+all:"medical"'
    """
    parts = [f'all:"{kw}"' for kw in keywords]
    return "+AND+".join(parts)


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    """Search arXiv for papers matching the query.

    Args:
        query: Search string (arXiv query format, e.g. 'all:"machine learning"').
        limit: Maximum number of papers to return.

    Returns:
        List of Paper objects. Returns empty list if the API fails.
    """
    params = {
        "search_query": query,
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        xml_text = response.text
    except Exception as e:
        print(f"[arXiv] API request failed: {e}")
        raise

    # Parse the Atom XML response
    root = ET.fromstring(xml_text)
    entries = root.findall("atom:entry", ATOM_NS)

    papers: List[Paper] = []

    for entry in entries:
        # Title
        title_el = entry.find("atom:title", ATOM_NS)
        title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else "Untitled"

        # Authors
        authors = []
        for author_el in entry.findall("atom:author", ATOM_NS):
            name_el = author_el.find("atom:name", ATOM_NS)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        # Abstract / summary
        summary_el = entry.find("atom:summary", ATOM_NS)
        abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else None

        # Published date -> year
        published_el = entry.find("atom:published", ATOM_NS)
        year = None
        if published_el is not None and published_el.text:
            try:
                year = int(published_el.text[:4])
            except (ValueError, IndexError):
                pass

        # arXiv ID from the <id> element (e.g. "http://arxiv.org/abs/2301.12345v1")
        id_el = entry.find("atom:id", ATOM_NS)
        arxiv_url = id_el.text.strip() if id_el is not None and id_el.text else None
        arxiv_id = None
        if arxiv_url:
            # Extract ID from URL like "http://arxiv.org/abs/2301.12345v1"
            parts = arxiv_url.split("/abs/")
            if len(parts) == 2:
                arxiv_id = parts[1]

        paper = Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source="arxiv",
            paper_id=arxiv_id,
            url=arxiv_url,
            citation_count=None,  # arXiv doesn't provide citation counts
            venue=None,
        )
        papers.append(paper)

    return papers
