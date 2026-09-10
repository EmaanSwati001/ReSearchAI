import requests
import json

payload = {
    "topic": "AI in healthcare",
    "experience_level": "beginner",
    "interest": "medical diagnosis",
}

print("Executing live Phase 5 E2E request to http://127.0.0.1:8000/research ...")
resp = requests.post("http://127.0.0.1:8000/research", json=payload, timeout=90)
print("HTTP Status:", resp.status_code)
data = resp.json()

print("\n--- 1. RESEARCH PLAN ---")
planner = data.get("planner_output", {})
print("Title:", planner.get("title"))
print("Keywords:", planner.get("keywords"))

print("\n--- 2. DISCOVERED PAPERS ---")
papers = data.get("papers", [])
print(f"Total papers discovered: {len(papers)}")
for i, p in enumerate(papers[:3], 1):
    print(f"  [{i}] [{p.get('source')}] {p.get('title')} ({p.get('year')})")

print("\n--- 3. ANALYZED PAPERS ---")
analysis_results = data.get("analysis_results", [])
print(f"Total papers analyzed: {len(analysis_results)}")
if analysis_results:
    print(f"  First paper title: {analysis_results[0].get('title')}")
    print(f"  Research problem: {analysis_results[0].get('research_problem')[:120]}...")

print("\n--- 4. IDENTIFIED RESEARCH GAPS ---")
gaps = data.get("gaps", [])
print(f"Total gaps identified: {len(gaps)}")
for i, g in enumerate(gaps, 1):
    print(f"\nGap #{i}:")
    print(f"  Gap: {g.get('gap')}")
    print(f"  Type: {g.get('gap_type')}")
    print(f"  Confidence: {g.get('confidence')}")
    print(f"  Supporting Papers: {g.get('supporting_papers')}")
    print(f"  Evidence: {g.get('evidence')[:150]}...")
    print(f"  Opportunity: {g.get('research_opportunity')[:150]}...")
