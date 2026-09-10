"""Real end-to-end test for Phase 3 — calls live APIs.

Run manually: python tests/test_e2e_discovery.py
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.agents.planner import run as planner_run
from backend.agents.discovery import run as discovery_run


def main():
    print("=" * 60)
    print("  ReSearchAI — Phase 3 End-to-End Test (LIVE APIs)")
    print("=" * 60)

    # Step 1: Simulate planner output
    state = {
        "user_topic": "AI in healthcare",
        "experience_level": "beginner",
        "user_interest": "Medical diagnosis",
    }

    print("\n[1] Running Planner Agent...")
    state = planner_run(state)
    planner = state.get("planner_output")

    if planner:
        print(f"    Title: {planner.get('title', 'N/A')}")
        print(f"    Keywords: {planner.get('keywords', [])}")
        print(f"    Subtopics: {planner.get('subtopics', [])}")
    else:
        print("    WARNING: Planner returned no output (GROQ_API_KEY may be missing).")
        print("    Using fallback planner output for discovery test...")
        state["planner_output"] = {
            "title": "AI for Early Disease Detection",
            "summary": "Research plan for AI in healthcare.",
            "keywords": ["machine learning", "medical diagnosis", "early disease detection"],
            "subtopics": ["imaging", "genomics"],
            "research_questions": ["How can ML improve diagnosis?"],
            "methodology_suggestions": ["systematic review"],
            "timeline_weeks": 8,
        }

    # Step 2: Run Discovery Agent
    print("\n[2] Running Discovery Agent (live API calls)...")
    state = discovery_run(state)

    papers = state.get("papers", [])
    errors = state.get("errors", [])

    print(f"\n[3] Results:")
    print(f"    Total papers discovered: {len(papers)}")

    if errors:
        print(f"    Errors encountered: {len(errors)}")
        for err in errors:
            print(f"      - {err}")

    # Count by source
    ss_count = sum(1 for p in papers if p.get("source") == "semantic_scholar")
    arxiv_count = sum(1 for p in papers if p.get("source") == "arxiv")
    print(f"    From Semantic Scholar: {ss_count}")
    print(f"    From arXiv: {arxiv_count}")

    # Show paper details
    if papers:
        print(f"\n{'=' * 60}")
        print("  DISCOVERED PAPERS")
        print(f"{'=' * 60}")
        for i, paper in enumerate(papers, 1):
            print(f"\n  [{i}] {paper.get('title', 'Untitled')}")
            print(f"      Source: {paper.get('source', '?')}")
            print(f"      Year: {paper.get('year', 'N/A')}")
            authors = paper.get('authors', [])
            if authors:
                print(f"      Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
            if paper.get('citation_count') is not None:
                print(f"      Citations: {paper['citation_count']}")
            if paper.get('url'):
                print(f"      URL: {paper['url']}")

    # Summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Planner output:        {'YES' if planner else 'FALLBACK'}")
    print(f"  Semantic Scholar:      {'OK' if ss_count > 0 else 'FAILED or empty'}")
    print(f"  arXiv:                 {'OK' if arxiv_count > 0 else 'FAILED or empty'}")
    print(f"  Total papers:          {len(papers)}")
    print(f"  Errors:                {len(errors)}")

    if len(papers) > 0:
        print("\n  [OK] END-TO-END TEST PASSED")
    else:
        print("\n  [!!] No papers found (APIs may be rate-limited or unreachable)")

    return len(papers) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
