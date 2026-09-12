import pytest
import os
import json
from unittest.mock import patch, MagicMock

from backend.schemas.roadmap import RoadmapResult
from backend.agents.roadmap import run, _call_groq_roadmap

def test_roadmap_schema_validation():
    """Test RoadmapResult schema validation."""
    valid_data = {
        "research_direction": "Test direction",
        "objective": "Test objective",
        "research_questions": ["Q1?"],
        "methodology": ["Step 1"],
        "data_requirements": ["Data"],
        "implementation_steps": ["Code"],
        "evaluation_metrics": ["Accuracy"],
        "expected_challenges": ["Time"],
        "expected_outcomes": ["Paper"],
        "validation_steps": ["Review"],
        "timeline_weeks": 4
    }
    result = RoadmapResult(**valid_data)
    assert result.timeline_weeks == 4
    
    # Test invalid timeline
    with pytest.raises(ValueError):
        RoadmapResult(**{**valid_data, "timeline_weeks": -1})

@patch("backend.agents.roadmap.requests.post")
def test_successful_roadmap_mocked_groq(mock_post):
    """Test successful roadmap generation for a supported gap."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "research_direction": "Confirmed Gap",
                        "objective": "Solve it.",
                        "research_questions": ["Q?"],
                        "methodology": ["M1"],
                        "data_requirements": ["D1"],
                        "implementation_steps": ["I1"],
                        "evaluation_metrics": ["E1"],
                        "expected_challenges": ["C1"],
                        "expected_outcomes": ["O1"],
                        "validation_steps": ["V1"],
                        "timeline_weeks": 8
                    })
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    state = {
        "gaps": [{"gap": "Strong Gap"}],
        "critic_results": [{"gap": "Strong Gap", "verdict": "Supported", "evidence_strength": "High"}],
    }
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result_state = run(state)
        
    assert "roadmap" in result_state
    assert result_state["roadmap"]["research_direction"] == "Confirmed Gap"
    assert result_state["roadmap"]["timeline_weeks"] == 8

@patch("backend.agents.roadmap.requests.post")
def test_weak_roadmap_mocked_groq(mock_post):
    """Negative test: Weak gap gets a validation roadmap."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "research_direction": "Pending Validation",
                        "objective": "Validate gap.",
                        "research_questions": ["Is this real?"],
                        "methodology": ["Search literature"],
                        "data_requirements": ["Papers"],
                        "implementation_steps": ["Search"],
                        "evaluation_metrics": ["Found papers"],
                        "expected_challenges": ["Time"],
                        "expected_outcomes": ["Clarity"],
                        "validation_steps": ["Read more"],
                        "timeline_weeks": 4
                    })
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    state = {
        "gaps": [{"gap": "Weak Gap"}],
        "critic_results": [{"gap": "Weak Gap", "verdict": "Weak / Needs More Evidence", "evidence_strength": "Low"}],
    }
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result_state = run(state)
        
    assert "roadmap" in result_state
    assert result_state["roadmap"]["research_direction"] == "Pending Validation"

def test_missing_api_key_creates_fallbacks():
    """Test missing API key uses fallback."""
    state = {
        "gaps": [{"gap": "Test Gap"}],
        "critic_results": [{"gap": "Test Gap"}]
    }
    with patch.dict(os.environ, {}, clear=True):
        result = run(state)
        assert result["roadmap"]["research_direction"] == "Pending further validation."

def test_empty_gaps_handled_safely():
    """Test empty gaps returns fallback roadmap."""
    state = {"gaps": []}
    result = run(state)
    assert result["roadmap"]["research_direction"] == "Pending further validation."

@patch("backend.agents.roadmap.requests.post")
def test_invalid_json_handled_safely(mock_post):
    """Test invalid LLM response handled safely."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is not JSON at all."}}]
    }
    mock_post.return_value = mock_response

    state = {
        "gaps": [{"gap": "Test Gap"}],
        "critic_results": [{"gap": "Test Gap"}]
    }
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result = run(state)
        assert result["roadmap"]["research_direction"] == "Pending further validation."
