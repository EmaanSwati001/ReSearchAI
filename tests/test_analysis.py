# tests/test_analysis.py

"""Tests for the Paper Analysis Agent (Phase 4).

All tests use mocked Groq API responses — no real network calls are made.
"""

from unittest.mock import patch, MagicMock
import json
import pytest

from backend.schemas.analysis import PaperAnalysis
from backend.agents import analysis


SAMPLE_PAPERS = [
    {
        "paper_id": "2301.00001",
        "title": "Machine Learning for Healthcare Diagnostics",
        "authors": ["Alice Smith", "Bob Jones"],
        "abstract": "We develop a convolutional neural network to diagnose diabetic retinopathy using retinal fundus images.",
        "year": 2023,
        "source": "arxiv",
    },
    {
        "paper_id": "2302.00002",
        "title": "Federated Learning in Clinical Trials",
        "authors": ["Carol White"],
        "abstract": "This work analyzes federated learning paradigms across decentralized hospital nodes without sharing raw patient data.",
        "year": 2022,
        "source": "arxiv",
    },
]

SAMPLE_GROQ_ANALYSIS_RESPONSE = {
    "paper_id": "2301.00001",
    "title": "Machine Learning for Healthcare Diagnostics",
    "research_problem": "Diagnosing diabetic retinopathy from retinal fundus images using deep learning.",
    "methodology": "Convolutional Neural Network (CNN) trained on fundus imagery.",
    "datasets": "Retinal fundus image dataset.",
    "key_findings": [
        "High diagnostic accuracy achieved for diabetic retinopathy.",
        "CNN architecture outperformed standard baselines."
    ],
    "limitations": "Not specified in the available abstract.",
    "future_work": "Not specified in the available abstract."
}


def _mock_groq_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if status_code == 200:
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(json_data)
                    }
                }
            ]
        }
    else:
        mock_resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock_resp


# ---------------------------------------------------------------------------
# 1. Schema validation
# ---------------------------------------------------------------------------
def test_paper_analysis_schema_validation():
    """Verify that PaperAnalysis validates proper fields and normalizes types."""
    data = {
        "paper_id": "123",
        "title": "A Test Study",
        "research_problem": "Investigate optimization.",
        "methodology": "Gradient descent variant.",
        "datasets": "Synthetic benchmarks.",
        "key_findings": ["Converged 2x faster."],
        "limitations": "Not specified in the available abstract.",
        "future_work": "Not specified in the available abstract.",
    }
    model = PaperAnalysis(**data)
    assert model.paper_id == "123"
    assert model.research_problem == "Investigate optimization."
    assert len(model.key_findings) == 1

    # Test normalization when string is provided for key_findings
    data_str_findings = data.copy()
    data_str_findings["key_findings"] = "Single finding string."
    model2 = PaperAnalysis(**data_str_findings)
    assert isinstance(model2.key_findings, list)
    assert model2.key_findings == ["Single finding string."]

    # Test normalization when None is passed
    data_none = data.copy()
    data_none["datasets"] = None
    model3 = PaperAnalysis(**data_none)
    assert model3.datasets == "Not specified in the available abstract."


# ---------------------------------------------------------------------------
# 2. Successful analysis with mocked Groq
# ---------------------------------------------------------------------------
@patch("backend.agents.analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_successful_analysis_mocked_groq(mock_post):
    """Verify successful analysis when Groq returns structured JSON."""
    mock_post.return_value = _mock_groq_response(SAMPLE_GROQ_ANALYSIS_RESPONSE)

    state = {"papers": [SAMPLE_PAPERS[0]]}
    result = analysis.run(state)

    assert "analysis_results" in result
    results = result["analysis_results"]
    assert len(results) == 1
    assert results[0]["paper_id"] == "2301.00001"
    assert results[0]["research_problem"] == SAMPLE_GROQ_ANALYSIS_RESPONSE["research_problem"]
    assert len(results[0]["key_findings"]) == 2
    assert results[0]["limitations"] == "Not specified in the available abstract."


# ---------------------------------------------------------------------------
# 3. Multiple papers produce multiple results
# ---------------------------------------------------------------------------
@patch("backend.agents.analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_multiple_papers_produce_multiple_results(mock_post):
    """Verify multiple papers are analyzed individually."""
    mock_post.return_value = _mock_groq_response(SAMPLE_GROQ_ANALYSIS_RESPONSE)

    state = {"papers": SAMPLE_PAPERS}
    result = analysis.run(state)

    results = result.get("analysis_results", [])
    assert len(results) == 2
    assert mock_post.call_count == 2


# ---------------------------------------------------------------------------
# 4. Empty or missing papers handled safely
# ---------------------------------------------------------------------------
def test_empty_papers_handled_safely():
    """Empty or missing papers in state should result in an empty analysis list."""
    state1 = {"papers": []}
    result1 = analysis.run(state1)
    assert result1["analysis_results"] == []

    state2 = {}
    result2 = analysis.run(state2)
    assert result2["analysis_results"] == []


# ---------------------------------------------------------------------------
# 5. Invalid LLM JSON handled safely
# ---------------------------------------------------------------------------
@patch("backend.agents.analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_invalid_llm_json_handled_safely(mock_post):
    """If Groq outputs non-JSON content, fallback analysis is used without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Sorry, I cannot produce JSON."}}]
    }
    mock_post.return_value = mock_resp

    state = {"papers": [SAMPLE_PAPERS[0]]}
    result = analysis.run(state)

    results = result["analysis_results"]
    assert len(results) == 1
    assert results[0]["paper_id"] == "2301.00001"
    assert "fallback" in results[0]["key_findings"][0].lower()


# ---------------------------------------------------------------------------
# 6. Groq failure on one paper does not crash the rest
# ---------------------------------------------------------------------------
@patch("backend.agents.analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_groq_failure_for_one_paper_does_not_crash(mock_post):
    """If one paper fails (e.g. 500 error), subsequent papers are still processed."""
    # First call fails, second call succeeds
    fail_resp = _mock_groq_response({}, status_code=500)
    success_resp = _mock_groq_response(SAMPLE_GROQ_ANALYSIS_RESPONSE, status_code=200)
    mock_post.side_effect = [fail_resp, success_resp]

    state = {"papers": SAMPLE_PAPERS}
    result = analysis.run(state)

    results = result["analysis_results"]
    assert len(results) == 2
    # First paper should have fallback
    assert "fallback" in results[0]["key_findings"][0].lower()
    # Second paper should have parsed response
    assert results[1]["research_problem"] == SAMPLE_GROQ_ANALYSIS_RESPONSE["research_problem"]


# ---------------------------------------------------------------------------
# 7. Missing API key generates fallbacks
# ---------------------------------------------------------------------------
@patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=True)
def test_missing_api_key_creates_fallbacks():
    """If GROQ_API_KEY is not configured, fallbacks are produced for all papers."""
    state = {"papers": [SAMPLE_PAPERS[0]]}
    result = analysis.run(state)

    results = result["analysis_results"]
    assert len(results) == 1
    assert "GROQ_API_KEY missing" in results[0]["key_findings"][0]
