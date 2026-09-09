# tests/test_graph.py

"""Tests for the LangGraph research graph scaffold."""

from backend.graph.research_graph import get_research_graph


def test_graph_construction_and_execution():
    graph = get_research_graph()
    # Minimal initial state matching the schema fields used.
    init_state = {
        "user_topic": "Artificial Intelligence",
        "experience_level": "beginner",
        "user_interest": "machine learning",
    }
    result = graph.invoke(init_state)
    # The final state should contain a status field.
    assert isinstance(result, dict)
    assert result.get("status") == "success"
    # Ensure no errors key present (optional).
    assert "errors" not in result or result["errors"] is None
