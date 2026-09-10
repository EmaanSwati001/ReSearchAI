# tests/test_gap_analysis.py

"""Tests for the Gap Analysis Agent (Phase 5).

All tests use mocked Groq API responses — no real network calls are made.
"""

from unittest.mock import patch, MagicMock
import json
import pytest

from backend.schemas.gap import ResearchGap
from backend.agents import gap_analysis


SAMPLE_ANALYZED_PAPERS = [
    {
        "paper_id": "P1",
        "title": "Deep Learning for Clinical Diagnosis",
        "research_problem": "Automated diagnosis in clinical settings",
        "methodology": "Convolutional Neural Networks",
        "datasets": "Dataset Alpha (single hospital)",
        "key_findings": ["High accuracy on local test set"],
        "limitations": "Limited evaluation on small datasets from a single cohort",
        "future_work": "Evaluation across multi-center hospitals",
    },
    {
        "paper_id": "P2",
        "title": "Transformer Models in Medical Imaging",
        "research_problem": "Scalable lesion classification",
        "methodology": "Vision Transformers",
        "datasets": "Dataset Beta (single center)",
        "key_findings": ["Outperformed CNN on curated benchmarks"],
        "limitations": "Limited evaluation on small datasets without external validation",
        "future_work": "Testing on diverse population cohorts",
    },
    {
        "paper_id": "P3",
        "title": "Federated Medical Diagnostics",
        "research_problem": "Privacy-preserving model training",
        "methodology": "Federated Averaging",
        "datasets": "Dataset Gamma (single site simulation)",
        "key_findings": ["Preserved patient privacy during training"],
        "limitations": "Limited evaluation on small datasets; lacks external clinical trial validation",
        "future_work": "Real-world multi-institutional deployment",
    },
]

SAMPLE_GAP_RESPONSE = {
    "gaps": [
        {
            "gap": "Within the reviewed papers, models are repeatedly evaluated only on single-center, small-scale datasets.",
            "evidence": "Papers P1, P2, and P3 each explicitly state that their evaluations are restricted to small single-cohort datasets lacking multi-center validation.",
            "supporting_papers": ["P1", "P2", "P3"],
            "gap_type": "Evaluation Gap",
            "confidence": "High",
            "research_opportunity": "Investigate cross-institutional generalization on diverse, multi-center real-world clinical benchmarks.",
        },
        {
            "gap": "Within the supplied literature, comparative benchmarking between Vision Transformers and Federated architectures is underexplored.",
            "evidence": "P2 evaluates Vision Transformers independently, while P3 explores Federated approaches without comparative performance analysis against transformer baselines.",
            "supporting_papers": ["P2", "P3"],
            "gap_type": "Methodology Gap",
            "confidence": "Medium",
            "research_opportunity": "Empirically compare transformer-based architectures under federated training constraints.",
        },
    ]
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
def test_research_gap_schema_validation():
    """Verify that ResearchGap validates correctly and normalizes fields."""
    data = {
        "gap": "Lack of prospective clinical trials.",
        "evidence": "All papers relied exclusively on retrospective datasets.",
        "supporting_papers": ["Paper1", "Paper2"],
        "gap_type": "Evaluation Gap",
        "confidence": "high",
        "research_opportunity": "Conduct prospective validation in hospital workflows.",
    }
    gap = ResearchGap(**data)
    assert gap.gap == "Lack of prospective clinical trials."
    assert gap.confidence == "High"
    assert len(gap.supporting_papers) == 2

    # Test confidence normalization for low/medium
    data_low = data.copy()
    data_low["confidence"] = "low confidence"
    gap_low = ResearchGap(**data_low)
    assert gap_low.confidence == "Low"

    # Test string for supporting_papers
    data_str_papers = data.copy()
    data_str_papers["supporting_papers"] = "Paper1"
    gap_str = ResearchGap(**data_str_papers)
    assert gap_str.supporting_papers == ["Paper1"]


# ---------------------------------------------------------------------------
# 2. Successful gap analysis with mocked Groq
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_successful_gap_analysis_mocked_groq(mock_post):
    """Verify gap analysis when Groq returns valid research gaps."""
    mock_post.return_value = _mock_groq_response(SAMPLE_GAP_RESPONSE)

    state = {
        "papers": SAMPLE_ANALYZED_PAPERS,
        "analysis_results": SAMPLE_ANALYZED_PAPERS,
    }
    result = gap_analysis.run(state)

    assert "gaps" in result
    gaps = result["gaps"]
    assert len(gaps) == 2
    assert gaps[0]["gap_type"] == "Evaluation Gap"
    assert gaps[0]["confidence"] == "High"
    assert "P1" in gaps[0]["supporting_papers"]


# ---------------------------------------------------------------------------
# 3. Multiple papers produce multiple gaps
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_multiple_papers_produce_multiple_gaps(mock_post):
    """Verify that multiple analyzed papers yield multiple identified gaps."""
    mock_post.return_value = _mock_groq_response(SAMPLE_GAP_RESPONSE)

    state = {
        "papers": SAMPLE_ANALYZED_PAPERS,
        "analysis_results": SAMPLE_ANALYZED_PAPERS,
    }
    result = gap_analysis.run(state)
    assert len(result["gaps"]) == 2


# ---------------------------------------------------------------------------
# 4. Empty papers handled safely
# ---------------------------------------------------------------------------
def test_empty_papers_handled_safely():
    """When papers list is empty, return gaps = [] without calling LLM."""
    state = {"papers": [], "analysis_results": []}
    result = gap_analysis.run(state)
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# 5. Empty analysis_results handled safely
# ---------------------------------------------------------------------------
def test_empty_analysis_results_handled_safely():
    """When analysis_results is missing or has < 2 items, gaps = []."""
    state = {"analysis_results": []}
    result = gap_analysis.run(state)
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# 6. Single paper does NOT produce unsupported cross-paper gaps
# ---------------------------------------------------------------------------
def test_single_paper_does_not_produce_cross_paper_gaps():
    """A single paper cannot justify cross-paper synthesis and should return empty gaps."""
    state = {
        "papers": [SAMPLE_ANALYZED_PAPERS[0]],
        "analysis_results": [SAMPLE_ANALYZED_PAPERS[0]],
    }
    result = gap_analysis.run(state)
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# 7. Invalid Groq JSON handled safely
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_invalid_groq_json_handled_safely(mock_post):
    """If Groq outputs invalid JSON, return empty gaps without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "This is not valid json {"}}]
    }
    mock_post.return_value = mock_resp

    state = {
        "papers": SAMPLE_ANALYZED_PAPERS,
        "analysis_results": SAMPLE_ANALYZED_PAPERS,
    }
    result = gap_analysis.run(state)
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# 8. Groq failure handled safely
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_groq_failure_handled_safely(mock_post):
    """If Groq request raises an exception (e.g. 500 error), workflow continues safely."""
    mock_post.side_effect = Exception("Groq connection failed")

    state = {
        "papers": SAMPLE_ANALYZED_PAPERS,
        "analysis_results": SAMPLE_ANALYZED_PAPERS,
    }
    result = gap_analysis.run(state)
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# 9. Safety Case: 3 papers with repeated limitation
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_repeated_limitation_pattern(mock_post):
    """Verify identification of repeated limitations across 3 papers."""
    repeated_limitation_response = {
        "gaps": [
            {
                "gap": "Repeated limited evaluation on small datasets.",
                "evidence": "Papers P1, P2, and P3 all explicitly report evaluations limited to small single-center datasets.",
                "supporting_papers": ["P1", "P2", "P3"],
                "gap_type": "Evaluation Gap",
                "confidence": "High",
                "research_opportunity": "Evaluate model architectures on multi-center heterogeneous datasets.",
            }
        ]
    }
    mock_post.return_value = _mock_groq_response(repeated_limitation_response)

    state = {
        "papers": SAMPLE_ANALYZED_PAPERS,
        "analysis_results": SAMPLE_ANALYZED_PAPERS,
    }
    result = gap_analysis.run(state)

    assert len(result["gaps"]) == 1
    gap = result["gaps"][0]
    assert gap["gap_type"] == "Evaluation Gap"
    assert "P1" in gap["supporting_papers"]
    assert "P2" in gap["supporting_papers"]
    assert "P3" in gap["supporting_papers"]


# ---------------------------------------------------------------------------
# 10. Contradiction Case
# ---------------------------------------------------------------------------
@patch("backend.agents.gap_analysis.requests.post")
@patch.dict("os.environ", {"GROQ_API_KEY": "fake_key", "GROQ_MODEL": "qwen/qwen3.8-27b"})
def test_contradiction_pattern(mock_post):
    """Verify identification of conflicting findings between papers."""
    contradiction_response = {
        "gaps": [
            {
                "gap": "Contradictory findings regarding the effectiveness of Method X in clinical diagnostics.",
                "evidence": "Paper A reports that Method X improves diagnostic accuracy by 15%, whereas Paper B concludes Method X does not improve performance over baseline.",
                "supporting_papers": ["Paper A", "Paper B"],
                "gap_type": "Contradiction",
                "confidence": "High",
                "research_opportunity": "Perform a standardized benchmark study investigating the exact conditions under which Method X succeeds or fails.",
            }
        ]
    }
    mock_post.return_value = _mock_groq_response(contradiction_response)

    contradictory_papers = [
        {
            "paper_id": "Paper A",
            "title": "Method X Improves Diagnosis",
            "research_problem": "Evaluating Method X",
            "methodology": "Method X",
            "datasets": "Dataset 1",
            "key_findings": ["Method X improves performance."],
            "limitations": "Not specified in the available abstract.",
            "future_work": "Not specified in the available abstract.",
        },
        {
            "paper_id": "Paper B",
            "title": "Method X Does Not Improve Performance",
            "research_problem": "Evaluating Method X",
            "methodology": "Method X",
            "datasets": "Dataset 2",
            "key_findings": ["Method X does not improve performance."],
            "limitations": "Not specified in the available abstract.",
            "future_work": "Not specified in the available abstract.",
        },
    ]

    state = {
        "papers": contradictory_papers,
        "analysis_results": contradictory_papers,
    }
    result = gap_analysis.run(state)

    assert len(result["gaps"]) == 1
    gap = result["gaps"][0]
    assert gap["gap_type"] == "Contradiction"
    assert "Paper A" in gap["supporting_papers"]
    assert "Paper B" in gap["supporting_papers"]
