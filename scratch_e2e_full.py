import asyncio
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.graph.research_graph import get_research_graph

def run_e2e():
    print("Starting ReSearchAI FULL E2E Test...\n")
    
    graph = get_research_graph()
    
    initial_state = {
        "user_topic": "AI in healthcare",
        "experience_level": "beginner",
        "user_interest": "medical diagnosis",
    }
    
    result = graph.invoke(initial_state)
    
    # Validation flags
    pass_planner = bool(result.get("planner_output"))
    pass_discovery = bool(result.get("papers") and len(result.get("papers")) > 0)
    
    # RAG validation: check if analysis results have evidence_sources
    analysis = result.get("analysis_results", [])
    pass_analysis = bool(analysis and len(analysis) > 0)
    
    pass_rag = False
    if pass_analysis:
        for a in analysis:
            if a.get("evidence_sources"):
                pass_rag = True
                break
                
    pass_gaps = bool(result.get("gaps") and len(result.get("gaps")) > 0)
    pass_critic = bool(result.get("critic_results") and len(result.get("critic_results")) > 0)
    pass_roadmap = bool(result.get("roadmap"))
    pass_finalize = bool(result.get("workflow_status") == "complete")

    print("\n========================================")
    print("ReSearchAI FULL E2E TEST")
    print("========================================")
    
    print(f"Planner:        {'PASS' if pass_planner else 'FAIL'}")
    print(f"Discovery:      {'PASS' if pass_discovery else 'FAIL'}")
    print(f"RAG:            {'PASS' if pass_rag else 'FAIL'}")
    print(f"Analysis:       {'PASS' if pass_analysis else 'FAIL'}")
    print(f"Gap Analysis:   {'PASS' if pass_gaps else 'FAIL'}")
    print(f"Critic:         {'PASS' if pass_critic else 'FAIL'}")
    print(f"Roadmap:        {'PASS' if pass_roadmap else 'FAIL'}")
    print(f"Finalize:       {'PASS' if pass_finalize else 'FAIL'}")

    print("\n========================================")
    print("FINAL OUTPUT")
    print("========================================\n")
    
    if pass_roadmap:
        print("Research Direction:")
        print(result["roadmap"].get("research_direction", "N/A"))
        print("\nRoadmap Timeline:")
        print(f"{result['roadmap'].get('timeline_weeks', 'N/A')} weeks")
        
    if pass_critic:
        print("\nCritic Verdict (Top Gap):")
        print(result["critic_results"][0].get("verdict", "N/A"))

if __name__ == "__main__":
    run_e2e()
