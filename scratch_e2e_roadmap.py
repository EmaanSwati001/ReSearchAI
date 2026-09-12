import asyncio
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.graph.research_graph import get_research_graph

def run_e2e():
    print("Starting E2E Roadmap Pipeline Test...")
    
    graph = get_research_graph()
    
    initial_state = {
        "user_topic": "AI in healthcare",
        "experience_level": "beginner",
        "user_interest": "medical diagnosis",
    }
    
    print(f"Initial state: {initial_state}")
    
    result = graph.invoke(initial_state)
    
    print("\n--- RESULTS ---")
    print(f"Status: {result.get('status')}")
    
    roadmap = result.get("roadmap", {})
    
    if not roadmap:
        print("\nERROR: No roadmap found in result state.")
        return
        
    print("\n==============================")
    print("RESEARCH ROADMAP")
    print("==============================\n")
    
    print("Research Direction:")
    print(roadmap.get("research_direction"))
    print("\nObjective:")
    print(roadmap.get("objective"))
    print("\nResearch Questions:")
    for rq in roadmap.get("research_questions", []):
        print(f"- {rq}")
    print("\nMethodology:")
    for i, m in enumerate(roadmap.get("methodology", []), 1):
        print(f"{i}. {m}")
    print("\nData Requirements:")
    for dr in roadmap.get("data_requirements", []):
        print(f"- {dr}")
    print("\nImplementation Steps:")
    for i, s in enumerate(roadmap.get("implementation_steps", []), 1):
        print(f"{i}. {s}")
    print("\nEvaluation Metrics:")
    for em in roadmap.get("evaluation_metrics", []):
        print(f"- {em}")
    print("\nExpected Challenges:")
    for ec in roadmap.get("expected_challenges", []):
        print(f"- {ec}")
    print("\nExpected Outcomes:")
    for eo in roadmap.get("expected_outcomes", []):
        print(f"- {eo}")
    print("\nValidation Steps:")
    for vs in roadmap.get("validation_steps", []):
        print(f"- {vs}")
    print(f"\nTimeline:\n{roadmap.get('timeline_weeks')} weeks")
    
    print("\nPhase 8 E2E Test Completed.")

if __name__ == "__main__":
    run_e2e()
