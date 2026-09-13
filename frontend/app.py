# frontend/app.py

"""Streamlit UI for ReSearchAI (updated for Phase 3).

Collects research topic, experience level, and optional interest,
sends a POST request to the FastAPI backend, and displays:
- The structured research plan from the Planner Agent
- The discovered papers from the Discovery Agent
"""

import streamlit as st
import requests
from typing import Dict

st.set_page_config(page_title="ReSearchAI", layout="centered")

st.title("ReSearchAI")
st.subheader("Your AI Research Mentor")

# Input fields
topic = st.text_input("Research topic", "")
experience = st.selectbox("Experience level", ["beginner", "intermediate", "expert"], index=0)
interest = st.text_input("Optional specific interest", "")

if st.button("Start Research"):
    if not topic:
        st.warning("Please enter a research topic.")
    else:
        payload = {
            "topic": topic,
            "experience_level": experience,
            "interest": interest if interest else None,
        }
        with st.spinner("Running research pipeline..."):
            try:
                response = requests.post(
                    "http://localhost:8000/research", json=payload, timeout=120
                )
                response.raise_for_status()
                data: Dict = response.json()
            except Exception as e:
                st.error(f"Error contacting backend: {e}")
                st.stop()

        st.success(f"Research workflow completed! Status: {data.get('status', 'unknown')}")

        # --- Research Plan ---
        planner_output = data.get("planner_output")
        if planner_output:
            st.markdown("---")
            st.header("📋 Research Plan")
            st.subheader(planner_output.get("title", ""))
            st.write(planner_output.get("summary", ""))

            keywords = planner_output.get("keywords", [])
            if keywords:
                st.markdown("**Keywords:** " + ", ".join(keywords))

            subtopics = planner_output.get("subtopics", [])
            if subtopics:
                st.markdown("**Subtopics:**")
                for sub in subtopics:
                    st.markdown(f"- {sub}")

            questions = planner_output.get("research_questions", [])
            if questions:
                st.markdown("**Research Questions:**")
                for q in questions:
                    st.markdown(f"- {q}")

            methods = planner_output.get("methodology_suggestions", [])
            if methods:
                st.markdown("**Methodology Suggestions:**")
                for m in methods:
                    st.markdown(f"- {m}")

            timeline = planner_output.get("timeline_weeks")
            if timeline:
                st.markdown(f"**Estimated Timeline:** {timeline} weeks")

        # --- Discovered Papers ---
        papers = data.get("papers", [])
        if papers:
            st.markdown("---")
            st.header(f"📄 Discovered Papers ({len(papers)})")

            for i, paper in enumerate(papers, 1):
                title = paper.get("title", "Untitled")
                source = paper.get("source", "unknown")
                year = paper.get("year")
                citation_count = paper.get("citation_count")

                # Header line with source badge
                year_str = f" ({year})" if year else ""
                source_badge = "🔵 Semantic Scholar" if source == "semantic_scholar" else "🟠 arXiv"
                st.subheader(f"{i}. {title}{year_str}")
                st.caption(f"Source: {source_badge}")

                # Authors
                authors = paper.get("authors", [])
                if authors:
                    st.markdown(f"**Authors:** {', '.join(authors)}")

                # Citation count (Semantic Scholar only)
                if citation_count is not None:
                    st.markdown(f"**Citations:** {citation_count}")

                # Venue
                venue = paper.get("venue")
                if venue:
                    st.markdown(f"**Venue:** {venue}")

                # URL
                url = paper.get("url")
                if url:
                    st.markdown(f"🔗 [View Paper]({url})")

                # Abstract in expander
                abstract = paper.get("abstract")
                if abstract:
                    with st.expander("Show Abstract"):
                        st.write(abstract)

                st.markdown("")  # Spacing between papers
        else:
            st.info("No papers were discovered. The search APIs may be unavailable.")

        # --- Paper Analysis (Phase 4) ---
        analysis_results = data.get("analysis_results", [])
        if analysis_results:
            st.markdown("---")
            st.header(f"📊 Paper Analysis ({len(analysis_results)})")
            st.caption("Analysis is grounded in retrieved evidence from the discovered research papers.")

            for i, analysis in enumerate(analysis_results, 1):
                paper_title = analysis.get("title") or f"Paper #{i}"
                with st.expander(f"📑 {i}. {paper_title}", expanded=(i <= 2)):
                    st.markdown(f"**🎯 Research Problem / Objective:**\n{analysis.get('research_problem', 'N/A')}")
                    st.markdown(f"**⚙️ Methodology:**\n{analysis.get('methodology', 'N/A')}")
                    st.markdown(f"**💾 Dataset / Data:**\n{analysis.get('datasets', 'N/A')}")

                    findings = analysis.get("key_findings", [])
                    st.markdown("**🔍 Key Findings:**")
                    if isinstance(findings, list) and findings:
                        for item in findings:
                            st.markdown(f"- {item}")
                    elif isinstance(findings, str) and findings:
                        st.markdown(findings)
                    else:
                        st.markdown("Not specified in the available abstract.")

                    st.markdown(f"**⚠️ Limitations:**\n{analysis.get('limitations', 'N/A')}")
                    st.markdown(f"**🚀 Future Work:**\n{analysis.get('future_work', 'N/A')}")
                    
                    evidence_sources = analysis.get("evidence_sources", [])
                    if evidence_sources:
                        st.markdown("---")
                        st.markdown("📚 **Evidence Used**")
                        st.caption(f"Based on {len(evidence_sources)} retrieved chunk(s).")
                        
                        unique_sources = {}
                        for chunk in evidence_sources:
                            source_url = chunk.get("url") or "#"
                            source_title = chunk.get("title") or "Unknown Paper"
                            src_type = chunk.get("source", "Unknown")
                            unique_sources[source_url] = (source_title, src_type)
                            
                        for url, (title, src_type) in unique_sources.items():
                            st.markdown(f"- [{title}]({url}) ({src_type})")

        # --- Research Gaps (Phase 5) ---
        gaps = data.get("gaps", [])
        if gaps:
            st.markdown("---")
            st.header(f"🔎 Research Gaps ({len(gaps)})")

            for i, gap_item in enumerate(gaps, 1):
                conf = str(gap_item.get("confidence", "Medium")).strip().capitalize()
                if conf == "High":
                    badge = "🟢 High Confidence"
                elif conf == "Low":
                    badge = "🔴 Low Confidence"
                else:
                    badge = "🟡 Medium Confidence"

                gap_type = gap_item.get("gap_type", "General Gap")
                gap_text = gap_item.get("gap", "Unnamed Gap")

                with st.expander(f"🔬 {i}. {gap_text} [{badge}]", expanded=(i <= 3)):
                    st.markdown(f"**🏷️ Gap Type:** `{gap_type}` | **Confidence:** {badge}")
                    st.markdown(f"**📌 Research Gap:**\n{gap_text}")
                    st.markdown(f"**🧾 Evidence:**\n{gap_item.get('evidence', 'N/A')}")

                    papers_list = gap_item.get("supporting_papers", [])
                    if papers_list:
                        st.markdown("**📚 Supporting Papers:**")
                        for sp in papers_list:
                            st.markdown(f"- {sp}")

                    st.markdown(f"**💡 Research Opportunity:**\n{gap_item.get('research_opportunity', 'N/A')}")

        # --- Research Critic (Phase 7) ---
        critic_results = data.get("critic_results", [])
        if critic_results:
            st.markdown("---")
            st.header(f"🧠 Research Critic ({len(critic_results)})")
            
            for i, crit in enumerate(critic_results, 1):
                verdict = crit.get("verdict", "Unknown")
                if "Partially" in verdict:
                    verdict_icon = "⚠️"
                elif "Weak" in verdict or "Needs" in verdict:
                    verdict_icon = "❌"
                else:
                    verdict_icon = "✅"
                    
                strength = crit.get("evidence_strength", "Unknown")
                if strength == "High":
                    str_icon = "💪"
                elif strength == "Medium":
                    str_icon = "⚖️"
                else:
                    str_icon = "📉"
                
                with st.expander(f"🧑‍🏫 Critic Evaluation #{i} - {verdict_icon} {verdict}", expanded=True):
                    st.markdown(f"**🔎 Research Gap:**\n{crit.get('gap', 'N/A')}")
                    st.markdown(f"**{verdict_icon} Verdict:** {verdict}")
                    st.markdown(f"**{str_icon} Evidence Strength:** {strength}")
                    st.markdown(f"**🧠 Reasoning:**\n{crit.get('reasoning', 'N/A')}")
                    st.markdown(f"**⚠️ Concerns:**\n{crit.get('concerns', 'N/A')}")
                    st.markdown(f"**💡 Recommendation:**\n{crit.get('recommendation', 'N/A')}")

        # --- Research Roadmap (Phase 8) ---
        roadmap = data.get("roadmap", {})
        if roadmap:
            st.markdown("---")
            st.header("🗺️ Research Roadmap")
            
            st.subheader("### Research Direction")
            st.write(roadmap.get("research_direction", "N/A"))
            
            st.subheader("### Objective")
            st.write(roadmap.get("objective", "N/A"))
            
            st.subheader("### Research Questions")
            for rq in roadmap.get("research_questions", []):
                st.write(f"- {rq}")
                
            st.subheader("### Methodology")
            for i, m in enumerate(roadmap.get("methodology", []), 1):
                st.write(f"{i}. {m}")
                
            st.subheader("### Data Requirements")
            for dr in roadmap.get("data_requirements", []):
                st.write(f"- {dr}")
                
            st.subheader("### Implementation Steps")
            for i, step in enumerate(roadmap.get("implementation_steps", []), 1):
                st.write(f"{i}. {step}")
                
            st.subheader("### Evaluation Metrics")
            for em in roadmap.get("evaluation_metrics", []):
                st.write(f"- {em}")
                
            st.subheader("### Expected Challenges")
            for ec in roadmap.get("expected_challenges", []):
                st.write(f"- {ec}")
                
            st.subheader("### Expected Outcomes")
            for eo in roadmap.get("expected_outcomes", []):
                st.write(f"- {eo}")
                
            st.subheader("### Validation Steps")
            for vs in roadmap.get("validation_steps", []):
                st.write(f"- {vs}")
                
            st.subheader("### Suggested Timeline")
            st.write(f"{roadmap.get('timeline_weeks', 'N/A')} weeks")
