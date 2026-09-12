import asyncio
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.graph.research_graph import get_research_graph

def run_e2e():
    print("Starting E2E Critic Pipeline Test...")
    
    # Initialize the LangGraph workflow with the request data.
    graph = get_research_graph()
    
    initial_state = {
        "user_topic": "AI in healthcare",
        "experience_level": "beginner",
        "user_interest": "medical diagnosis",
    }
    
    print(f"Initial state: {initial_state}")
    
    # Run the graph synchronously.
    result = graph.invoke(initial_state)
    
    print("\n--- RESULTS ---")
    print(f"Status: {result.get('status')}")
    
    papers = result.get('papers', [])
    print(f"\nDiscovered Papers: {len(papers)}")
        
    analysis_results = result.get('analysis_results', [])
    print(f"\nAnalysis Results: {len(analysis_results)}")
    
    gaps = result.get('gaps', [])
    print(f"\nResearch Gaps: {len(gaps)}")
    
    critic_results = result.get('critic_results', [])
    print(f"\nCritic Results: {len(critic_results)}")
    
    for i, c in enumerate(critic_results):
        print(f"\n  Critic Result {i+1}:")
        print(f"  Gap: {c.get('gap')}")
        print(f"  Verdict: {c.get('verdict')} (Strength: {c.get('evidence_strength')})")
        print(f"  Reasoning: {c.get('reasoning')}")
        print(f"  Concerns: {c.get('concerns')}")
        print(f"  Recommendation: {c.get('recommendation')}")
            
    print("\nPhase 7 E2E Test Completed.")

if __name__ == "__main__":
    run_e2e()
