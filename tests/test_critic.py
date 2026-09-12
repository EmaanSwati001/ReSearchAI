import pytest
import os
import json
from unittest.mock import patch, MagicMock

from backend.schemas.critic import CriticResult
from backend.agents.critic import run, _call_groq_critic

def test_critic_schema_validation():
    """Test CriticResult schema validation."""
    valid_data = {
        "gap": "Test gap",
        "verdict": "Supported",
        "evidence_strength": "High",
        "reasoning": "Reasoning here.",
        "concerns": "No concerns.",
        "recommendation": "Do nothing."
    }
    result = CriticResult(**valid_data)
    assert result.verdict == "Supported"
    
    # Test invalid literal
    with pytest.raises(ValueError):
        CriticResult(**{**valid_data, "verdict": "Definitely True"})

@patch("backend.agents.critic.requests.post")
def test_successful_critic_mocked_groq(mock_post):
    """Test successful gap evaluation."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "gap": "Test Gap",
                        "verdict": "Supported",
                        "evidence_strength": "High",
                        "reasoning": "Matches paper A.",
                        "concerns": "None",
                        "recommendation": "Proceed."
                    })
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    state = {
        "gaps": [{"gap": "Test Gap", "evidence": "Some evidence"}],
        "analysis_results": [{"title": "Paper A", "research_problem": "Test"}],
        "papers": []
    }
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result_state = run(state)
        
    assert "critic_results" in result_state
    assert len(result_state["critic_results"]) == 1
    assert result_state["critic_results"][0]["verdict"] == "Supported"
    assert result_state["critic_results"][0]["evidence_strength"] == "High"

@patch("backend.agents.critic.requests.post")
def test_negative_critic_mocked_groq(mock_post):
    """Negative test: Weak gap gets rejected."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "gap": "No researchers have studied X.",
                        "verdict": "Weak / Needs More Evidence",
                        "evidence_strength": "Low",
                        "reasoning": "The provided papers do not support this broad claim.",
                        "concerns": "Overgeneralization.",
                        "recommendation": "Search more literature."
                    })
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    state = {
        "gaps": [{"gap": "No researchers have studied X.", "evidence": "Papers don't mention X"}],
        "analysis_results": [],
        "papers": []
    }
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result_state = run(state)
        
    assert "critic_results" in result_state
    assert result_state["critic_results"][0]["verdict"] == "Weak / Needs More Evidence"
    assert result_state["critic_results"][0]["evidence_strength"] == "Low"

def test_missing_api_key_creates_fallbacks():
    """Test missing API key uses fallback."""
    state = {
        "gaps": [{"gap": "Test Gap"}]
    }
    with patch.dict(os.environ, {}, clear=True):
        result = run(state)
        assert len(result["critic_results"]) == 1
        assert result["critic_results"][0]["verdict"] == "Weak / Needs More Evidence"
        assert result["critic_results"][0]["evidence_strength"] == "Low"

def test_empty_gaps_handled_safely():
    """Test empty gaps returns empty results."""
    state = {"gaps": []}
    result = run(state)
    assert result["critic_results"] == []

@patch("backend.agents.critic.requests.post")
def test_invalid_json_handled_safely(mock_post):
    """Test invalid LLM response handled safely."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is not JSON at all."}}]
    }
    mock_post.return_value = mock_response

    state = {"gaps": [{"gap": "Test Gap"}]}
    
    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy"}):
        result = run(state)
        assert len(result["critic_results"]) == 1
        assert result["critic_results"][0]["reasoning"] == "Critic evaluation unavailable (Groq request failed)."
