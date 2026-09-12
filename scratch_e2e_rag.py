import asyncio
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.graph.research_graph import get_research_graph
import backend.config

def run_e2e():
    print("Starting E2E RAG Pipeline Test...")
    
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
    for i, p in enumerate(papers):
        print(f"  {i+1}. {p.get('title')}")
        
    analysis_results = result.get('analysis_results', [])
    print(f"\nAnalysis Results: {len(analysis_results)}")
    
    for i, a in enumerate(analysis_results):
        print(f"\n  Analysis {i+1}: {a.get('title')}")
        print(f"  Research Problem: {a.get('research_problem')}")
        print(f"  Datasets: {a.get('datasets')}")
        
        evidence = a.get('evidence_sources', [])
        print(f"  Evidence sources used: {len(evidence)}")
        if evidence:
            print(f"    - First source: {evidence[0].get('title')} ({evidence[0].get('source')})")
            
    print("\nPhase 6 E2E Test Completed.")

if __name__ == "__main__":
    run_e2e()
