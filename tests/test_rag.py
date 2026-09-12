import pytest
from backend.rag.loader import get_paper_content
from backend.rag.chunker import chunk_text
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever
from backend.agents.analysis import _call_groq_analysis
import os
from unittest.mock import patch, MagicMock
import json

def test_loader_fallback():
    """Test that missing full text falls back to abstract."""
    paper = {
        "title": "Test Title",
        "abstract": "This is a test abstract.",
    }
    content = get_paper_content(paper)
    assert "Title: Test Title" in content
    assert "Abstract: This is a test abstract." in content

def test_loader_empty():
    """Test empty document is handled safely."""
    content = get_paper_content({})
    assert content == ""

def test_chunker():
    """Test text is correctly chunked and metadata preserved."""
    paper = {
        "paper_id": "123",
        "title": "Chunking Test",
        "source": "arxiv",
        "url": "http://arxiv.org/abs/123"
    }
    text = "Sentence one. Sentence two. Sentence three."
    
    # Use very small chunk size to force split
    chunks = chunk_text(text, paper, chunk_size=15, chunk_overlap=0)
    
    assert len(chunks) > 1
    assert chunks[0]["paper_id"] == "123"
    assert chunks[0]["title"] == "Chunking Test"
    assert chunks[0]["source"] == "arxiv"
    assert chunks[0]["url"] == "http://arxiv.org/abs/123"
    assert chunks[0]["chunk_index"] == 0

def test_chunker_empty():
    """Test chunking empty text."""
    chunks = chunk_text("", {})
    assert chunks == []

@pytest.fixture(scope="module")
def vector_store():
    """Initialize a single vector store for testing to save time."""
    return VectorStore()

def test_vector_store_and_retrieval(vector_store):
    """Test embeddings, addition, and retrieval."""
    paper = {"paper_id": "456", "title": "Retrieval Test"}
    text = (
        "The study evaluates the proposed model using the MIMIC-III dataset. "
        "We achieved state-of-the-art results on several benchmarks. "
        "One limitation is the high computational cost."
    )
    
    chunks = chunk_text(text, paper, chunk_size=100, chunk_overlap=10)
    
    # Add chunks
    vector_store.add_chunks(chunks)
    assert vector_store.index.ntotal > 0
    
    # Retrieve
    retriever = Retriever(vector_store)
    
    # Query specifically for dataset
    results = retriever.retrieve_relevant_evidence("What dataset was used in this study?", k=1)
    assert len(results) == 1
    assert "MIMIC-III dataset" in results[0]["text"]
    assert "similarity_score" in results[0]

@patch("backend.agents.analysis.requests.post")
def test_rag_grounding(mock_post):
    """RAG Grounding test to ensure LLM uses retrieved evidence."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    
    mock_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "research_problem": "Test Problem",
                        "methodology": "Test Method",
                        "datasets": "MIMIC-III",
                        "key_findings": ["Test finding"],
                        "limitations": "Not specified in the available evidence.",
                        "future_work": "Not specified in the available evidence."
                    })
                }
            }
        ]
    }
    mock_response.json.return_value = mock_json
    mock_post.return_value = mock_response

    # Simulated retrieved evidence
    evidence = [
        {"text": "The study evaluates the proposed model using the MIMIC-III dataset.", "url": "mock"}
    ]
    
    paper = {"title": "Test Paper", "paper_id": "test_id"}
    
    result = _call_groq_analysis("dummy-model", "dummy-key", paper, evidence)
    
    # Verify grounding behavior
    assert result["datasets"] == "MIMIC-III"
    assert result["limitations"] == "Not specified in the available evidence."
    assert "evidence_sources" in result
    assert result["evidence_sources"] == evidence
    
    # Verify prompt included evidence
    call_kwargs = mock_post.call_args.kwargs
    payload = call_kwargs["json"]
    user_content = payload["messages"][1]["content"]
    assert "RETRIEVED EVIDENCE" in user_content
    assert "MIMIC-III dataset" in user_content
