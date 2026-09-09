# tests/test_discovery.py

"""Tests for the Paper Discovery Agent (Phase 3).

All tests use mocked API responses — no real network calls are made.
"""

from unittest.mock import patch, MagicMock
import json

import pytest

from backend.schemas.paper import Paper
from backend.tools import semantic_scholar, arxiv
from backend.agents import discovery


# ---------------------------------------------------------------------------
# Sample API responses for mocking
# ---------------------------------------------------------------------------

SAMPLE_SS_RESPONSE = {
    "total": 2,
    "data": [
        {
            "paperId": "abc123",
            "title": "Machine Learning for Medical Diagnosis",
            "authors": [{"authorId": "1", "name": "Alice Smith"}],
            "abstract": "This paper explores ML in healthcare.",
            "year": 2023,
            "url": "https://www.semanticscholar.org/paper/abc123",
            "citationCount": 42,
            "venue": "NeurIPS",
            "externalIds": {"ArXiv": "2301.00001"},
        },
        {
            "paperId": "def456",
            "title": "Deep Learning in Clinical Settings",
            "authors": [
                {"authorId": "2", "name": "Bob Jones"},
                {"authorId": "3", "name": "Carol Lee"},
            ],
            "abstract": "A survey of deep learning methods.",
            "year": 2022,
            "url": "https://www.semanticscholar.org/paper/def456",
            "citationCount": 15,
            "venue": "ICML",
            "externalIds": {},
        },
    ],
}

SAMPLE_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <title>Machine Learning for Medical Diagnosis</title>
    <summary>This paper explores ML in healthcare.</summary>
    <published>2023-01-15T00:00:00Z</published>
    <author><name>Alice Smith</name></author>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2302.99999v1</id>
    <title>Neural Networks for Drug Discovery</title>
    <summary>An overview of neural network applications.</summary>
    <published>2023-02-20T00:00:00Z</published>
    <author><name>Dave Wilson</name></author>
    <author><name>Eve Brown</name></author>
  </entry>
</feed>
"""

SAMPLE_PLANNER_OUTPUT = {
    "title": "AI for Early Disease Detection",
    "summary": "Research plan for AI in healthcare.",
    "keywords": ["machine learning", "medical diagnosis", "early disease detection"],
    "subtopics": ["imaging", "genomics"],
    "research_questions": ["How can ML improve diagnosis?"],
    "methodology_suggestions": ["systematic review"],
    "timeline_weeks": 8,
}


# ---------------------------------------------------------------------------
# Tests: Semantic Scholar tool
# ---------------------------------------------------------------------------

class TestSemanticScholar:
    """Tests for the Semantic Scholar search tool."""

    @patch("backend.tools.semantic_scholar.requests.get")
    def test_successful_search(self, mock_get):
        """Semantic Scholar returns valid papers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SS_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        papers = semantic_scholar.search_papers("machine learning medical", limit=10)

        assert len(papers) == 2
        assert papers[0].title == "Machine Learning for Medical Diagnosis"
        assert papers[0].source == "semantic_scholar"
        assert papers[0].paper_id == "abc123"
        assert papers[0].citation_count == 42
        assert papers[0].authors == ["Alice Smith"]

    @patch("backend.tools.semantic_scholar.requests.get")
    def test_api_failure_raises(self, mock_get):
        """Semantic Scholar API failure raises an exception."""
        mock_get.side_effect = Exception("Connection timeout")

        with pytest.raises(Exception, match="Connection timeout"):
            semantic_scholar.search_papers("test query")

    @patch("backend.tools.semantic_scholar.requests.get")
    def test_empty_results(self, mock_get):
        """Semantic Scholar returns no papers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total": 0, "data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        papers = semantic_scholar.search_papers("obscure topic xyz")
        assert papers == []


# ---------------------------------------------------------------------------
# Tests: arXiv tool
# ---------------------------------------------------------------------------

class TestArxiv:
    """Tests for the arXiv search tool."""

    @patch("backend.tools.arxiv.requests.get")
    def test_successful_search(self, mock_get):
        """arXiv returns valid papers from XML."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_ARXIV_XML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        papers = arxiv.search_papers('all:"machine learning"', limit=10)

        assert len(papers) == 2
        assert papers[0].title == "Machine Learning for Medical Diagnosis"
        assert papers[0].source == "arxiv"
        assert papers[0].paper_id == "2301.00001v1"
        assert papers[0].year == 2023
        assert papers[1].authors == ["Dave Wilson", "Eve Brown"]

    @patch("backend.tools.arxiv.requests.get")
    def test_api_failure_raises(self, mock_get):
        """arXiv API failure raises an exception."""
        mock_get.side_effect = Exception("503 Service Unavailable")

        with pytest.raises(Exception, match="503"):
            arxiv.search_papers('all:"test"')

    def test_build_query(self):
        """arXiv query builder creates correct format."""
        query = arxiv._build_query(["machine learning", "healthcare"])
        assert query == 'all:"machine learning"+AND+all:"healthcare"'

    def test_build_query_single_keyword(self):
        """arXiv query builder works with a single keyword."""
        query = arxiv._build_query(["AI"])
        assert query == 'all:"AI"'


# ---------------------------------------------------------------------------
# Tests: Deduplication
# ---------------------------------------------------------------------------

class TestDeduplication:
    """Tests for the paper deduplication logic."""

    def test_removes_duplicate_by_title(self):
        """Papers with the same normalized title are deduplicated."""
        papers = [
            Paper(title="Machine Learning for Medical Diagnosis", source="semantic_scholar", authors=[]),
            Paper(title="machine learning for medical diagnosis", source="arxiv", authors=[]),
        ]
        result = discovery._deduplicate_papers(papers)
        assert len(result) == 1
        assert result[0].source == "semantic_scholar"  # First one kept

    def test_removes_duplicate_by_id(self):
        """Papers with the same paper_id are deduplicated."""
        papers = [
            Paper(title="Paper A", source="semantic_scholar", paper_id="123", authors=[]),
            Paper(title="Paper A (extended)", source="arxiv", paper_id="123", authors=[]),
        ]
        result = discovery._deduplicate_papers(papers)
        assert len(result) == 1

    def test_keeps_unique_papers(self):
        """Unique papers are all kept."""
        papers = [
            Paper(title="Paper A", source="semantic_scholar", authors=[]),
            Paper(title="Paper B", source="arxiv", authors=[]),
            Paper(title="Paper C", source="semantic_scholar", authors=[]),
        ]
        result = discovery._deduplicate_papers(papers)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# Tests: Discovery Agent
# ---------------------------------------------------------------------------

class TestDiscoveryAgent:
    """Tests for the full Discovery Agent run function."""

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_stores_papers_in_state(self, mock_ss, mock_arxiv):
        """Discovery agent stores papers in state['papers']."""
        mock_ss.return_value = [
            Paper(title="SS Paper", source="semantic_scholar", authors=["Author A"]),
        ]
        mock_arxiv.return_value = [
            Paper(title="arXiv Paper", source="arxiv", authors=["Author B"]),
        ]

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        result = discovery.run(state)

        assert "papers" in result
        assert len(result["papers"]) == 2
        assert result["papers"][0]["title"] == "SS Paper"
        assert result["papers"][1]["title"] == "arXiv Paper"

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_combines_and_deduplicates(self, mock_ss, mock_arxiv):
        """Discovery agent deduplicates papers from both sources."""
        mock_ss.return_value = [
            Paper(title="Same Paper Title", source="semantic_scholar", authors=[]),
        ]
        mock_arxiv.return_value = [
            Paper(title="Same Paper Title", source="arxiv", authors=[]),
        ]

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        result = discovery.run(state)

        assert len(result["papers"]) == 1

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_handles_ss_failure(self, mock_ss, mock_arxiv):
        """If Semantic Scholar fails, arXiv results are still returned."""
        mock_ss.side_effect = Exception("SS is down")
        mock_arxiv.return_value = [
            Paper(title="arXiv Paper", source="arxiv", authors=[]),
        ]

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        result = discovery.run(state)

        assert len(result["papers"]) == 1
        assert result["papers"][0]["source"] == "arxiv"
        assert any("Semantic Scholar failed" in e for e in result.get("errors", []))

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_handles_arxiv_failure(self, mock_ss, mock_arxiv):
        """If arXiv fails, Semantic Scholar results are still returned."""
        mock_ss.return_value = [
            Paper(title="SS Paper", source="semantic_scholar", authors=[]),
        ]
        mock_arxiv.side_effect = Exception("arXiv is down")

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        result = discovery.run(state)

        assert len(result["papers"]) == 1
        assert result["papers"][0]["source"] == "semantic_scholar"
        assert any("arXiv failed" in e for e in result.get("errors", []))

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_handles_both_failures(self, mock_ss, mock_arxiv):
        """If both APIs fail, papers is an empty list with errors."""
        mock_ss.side_effect = Exception("SS is down")
        mock_arxiv.side_effect = Exception("arXiv is down")

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        result = discovery.run(state)

        assert result["papers"] == []
        assert len(result.get("errors", [])) == 2

    def test_no_planner_output(self):
        """If there is no planner output, papers is an empty list."""
        state = {}
        result = discovery.run(state)

        assert result["papers"] == []

    @patch("backend.agents.discovery.arxiv.search_papers")
    @patch("backend.agents.discovery.semantic_scholar.search_papers")
    def test_extract_search_query(self, mock_ss, mock_arxiv):
        """Search query is built from planner keywords."""
        mock_ss.return_value = []
        mock_arxiv.return_value = []

        state = {"planner_output": SAMPLE_PLANNER_OUTPUT}
        discovery.run(state)

        # Check what query was passed to Semantic Scholar
        call_args = mock_ss.call_args
        query = call_args[0][0]  # First positional argument
        assert "machine learning" in query
        assert "medical diagnosis" in query
