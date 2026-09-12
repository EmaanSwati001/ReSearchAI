# backend/rag/loader.py
import re
from typing import Dict, Any

def get_paper_content(paper: Dict[str, Any]) -> str:
    """Extract text content from a paper. 
    Currently falls back to abstract as full-text fetching is not fully integrated/required yet.
    """
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    
    # In a full version, we might fetch arXiv PDF text here.
    # For now, we use title and abstract to ensure it runs without external dependencies.
    content_parts = []
    if title:
        content_parts.append(f"Title: {title}")
    if abstract:
        content_parts.append(f"Abstract: {abstract}")
        
    return "\n\n".join(content_parts)
