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
                    "http://localhost:8000/research", json=payload, timeout=60
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
