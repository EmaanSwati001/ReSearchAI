# frontend/app.py

"""ReSearchAI - Autonomous AI Research Mentor & Capstone Platform.

Modern, multi-agent Streamlit interface featuring:
- Hero banner & custom CSS design system
- Multi-Agent Orchestration Visualizer
- Interactive Tabbed Dashboard (Roadmap, Gaps & Critic, Analysis, Literature RAG, Plan)
- Preset Research Topic Templates
- Full Dossier Export (Markdown & JSON)
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any

# Page Configuration
st.set_page_config(
    page_title="ReSearchAI | AI Research Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for High-Contrast Capstone Design
st.markdown("""
<style>
    /* Hide white Streamlit headers and toolbars */
    header[data-testid="stHeader"], .stAppHeader {
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
    }
    
    /* Global Background & High-Contrast Typography */
    .stApp, div[data-testid="stToolbar"] {
        background-color: #0b0f19 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Force crisp white/light text on all standard elements */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp li, .stApp label, .stMarkdown, .stMarkdown p {
        color: #f8fafc !important;
        font-size: 1rem;
    }
    
    /* Headings & Accent Color */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #38bdf8 !important;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        color: #cbd5e1 !important;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    /* Agent Pipeline Status Badges */
    .agent-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .agent-name {
        font-weight: 600;
        color: #f8fafc !important;
        font-size: 0.9rem;
    }
    .agent-status {
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
    }
    .status-active { background: #0284c7; color: #ffffff !important; }
    .status-done { background: #15803d; color: #ffffff !important; }
    .status-pending { background: #475569; color: #cbd5e1 !important; }
    
    /* Metric Cards */
    .metric-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8 !important;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #cbd5e1 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Expanders & Callout Customization */
    div[data-testid="stExpander"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 0.8rem !important;
    }
    div[data-testid="stExpander"] * {
        color: #f8fafc !important;
    }
    .stAlert, .stAlert p {
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
        color: #f8fafc !important;
        border-radius: 12px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: #cbd5e1 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
    
    /* Step Cards */
    .step-card {
        background: #1e293b !important;
        border-left: 4px solid #38bdf8 !important;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #f8fafc !important;
    }
    .step-card * {
        color: #f8fafc !important;
    }
    .step-title {
        font-weight: 700;
        color: #38bdf8 !important;
    }

    /* Buttons & Download Buttons */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }
    .stButton > button *, .stDownloadButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        border-color: #7dd3fc !important;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar & Configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 ReSearchAI")
    st.caption("⚡ LangGraph Orchestrated Multi-Agent Architecture")
    
    st.markdown("---")
    st.subheader("💡 Topic Templates")
    st.caption("Click a preset to quickly evaluate the capstone demo:")
    
    preset_topics = {
        "AI Healthcare": "AI-driven Early Disease Diagnosis & Medical Imaging",
        "LLM Hallucinations": "Mitigating Hallucinations in LLMs via Retrieval-Augmented Generation",
        "Quantum ML": "Quantum Machine Learning Algorithms for Drug Discovery",
        "Robot Swarms": "Autonomous Navigation & Consensus in Robot Swarms"
    }
    
    selected_preset = st.radio("Select Preset Topic:", ["Custom Topic"] + list(preset_topics.keys()))
    
    st.markdown("---")
    st.subheader("🤖 Active Agent Pipeline")
    
    agents = [
        ("🧠 Planner Agent", "Parses intent & structures strategy"),
        ("🔍 Discovery Agent", "Queries Semantic Scholar & arXiv"),
        ("📚 Vector RAG Engine", "Indexes FAISS chunks & embeds"),
        ("📊 Analysis Agent", "Extracts methods & limitations"),
        ("🔎 Gap Analysis Agent", "Identifies cross-paper gaps"),
        ("🧑‍🏫 Research Critic", "Rigorously evaluates evidence"),
        ("🗺️ Roadmap Agent", "Synthesizes step-by-step plan")
    ]
    
    for name, desc in agents:
        st.markdown(f"""
        <div class="agent-card">
            <div>
                <div class="agent-name">{name}</div>
                <div style="font-size:0.75rem; color:#94a3b8;">{desc}</div>
            </div>
            <span class="agent-status status-done">Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.caption("📌 Capstone Project | Autonomous Research Agent Workflow")

# ---------------------------------------------------------------------------
# Hero Header & Inputs
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎓 ReSearchAI: Autonomous AI Research Mentor</div>
    <div class="hero-subtitle">Move from a broad topic to literature-backed research gaps, critical peer evaluations, and an actionable execution roadmap.</div>
</div>
""", unsafe_allow_html=True)

# Determine default input from preset
default_topic_text = ""
if selected_preset != "Custom Topic":
    default_topic_text = preset_topics[selected_preset]

col_in1, col_in2, col_in3 = st.columns([3, 1.5, 2])

with col_in1:
    topic_input = st.text_input("🔬 Enter Research Topic", value=default_topic_text, placeholder="e.g. Machine Learning for Climate Forecasting")

with col_in2:
    experience_input = st.selectbox("🎓 Target Skill Level", ["beginner", "intermediate", "expert"], index=0)

with col_in3:
    interest_input = st.text_input("🎯 Specific Focus (Optional)", placeholder="e.g. Graph Neural Networks")

st.markdown("<br>", unsafe_allow_html=True)
start_button = st.button("🚀 Launch Multi-Agent Workflow", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Pipeline Execution & Data Retrieval
# ---------------------------------------------------------------------------
if start_button:
    if not topic_input.strip():
        st.warning("⚠️ Please enter a research topic to proceed.")
    else:
        # Progress visualizer
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        status_box.info("🧠 **Planner Agent:** Formulating structured research strategy...")
        progress_bar.progress(15)
        time.sleep(0.3)
        
        status_box.info("🔍 **Discovery Agent:** Searching Semantic Scholar & arXiv literature databases...")
        progress_bar.progress(35)
        
        payload = {
            "topic": topic_input,
            "experience_level": experience_input,
            "interest": interest_input if interest_input.strip() else None,
        }
        
        try:
            start_time = time.time()
            response = requests.post("http://localhost:8000/research", json=payload, timeout=300)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            elapsed = time.time() - start_time
            
            progress_bar.progress(100)
            status_box.success(f"✅ Multi-Agent Workflow Executed Successfully in {elapsed:.1f}s!")
            time.sleep(0.5)
            status_box.empty()
            progress_bar.empty()
            
            st.session_state["research_data"] = data
            st.session_state["research_topic"] = topic_input
        except Exception as e:
            progress_bar.empty()
            status_box.error(f"❌ Backend Request Error: {e}")
            st.stop()

# Render Results Dashboard if available in state
if "research_data" in st.session_state:
    data = st.session_state["research_data"]
    topic_name = st.session_state.get("research_topic", topic_input)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Overview Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(data.get("papers", []))}</div><div class="metric-lbl">Papers Found</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(data.get("analysis_results", []))}</div><div class="metric-lbl">RAG Analyzed</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(data.get("gaps", []))}</div><div class="metric-lbl">Gaps Identified</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(data.get("critic_results", []))}</div><div class="metric-lbl">Peer Critic Reviews</div></div>', unsafe_allow_html=True)
    with m5:
        roadmap_time = data.get("roadmap", {}).get("timeline_weeks", "4")
        st.markdown(f'<div class="metric-box"><div class="metric-val">{roadmap_time}w</div><div class="metric-lbl">Est. Timeline</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Dashboard Tabs
    tab_roadmap, tab_gaps, tab_analysis, tab_papers, tab_plan = st.tabs([
        "🗺️ Actionable Roadmap",
        "🔎 Gaps & Critic Evaluation",
        "📊 RAG Deep Analysis",
        "📄 Literature Discovery",
        "📋 Research Strategy"
    ])
    
    # -----------------------------------------------------------------------
    # TAB 1: Actionable Roadmap
    # -----------------------------------------------------------------------
    with tab_roadmap:
        roadmap = data.get("roadmap", {})
        if roadmap:
            st.markdown(f"### 🗺️ Research Roadmap for *'{topic_name}'*")
            
            st.info(f"**📌 Primary Research Direction:**\n\n{roadmap.get('research_direction', 'N/A')}")
            
            st.markdown(f"**🎯 Core Objective:** {roadmap.get('objective', 'N/A')}")
            st.markdown("<br>", unsafe_allow_html=True)
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.subheader("❓ Key Research Questions")
                for rq in roadmap.get("research_questions", []):
                    st.markdown(f"- 🔹 {rq}")
                    
                st.subheader("🔬 Methodology & Technical Approach")
                for m in roadmap.get("methodology", []):
                    clean_m = str(m).lstrip("0123456789. ")
                    st.markdown(f"- ⚙️ {clean_m}")

            with r_col2:
                st.subheader("💾 Data & Compute Requirements")
                for dr in roadmap.get("data_requirements", []):
                    st.markdown(f"- 📊 {dr}")
                    
                st.subheader("📈 Evaluation & Success Metrics")
                for em in roadmap.get("evaluation_metrics", []):
                    st.markdown(f"- 🎯 {em}")

            st.markdown("---")
            st.subheader("🚀 Step-by-Step Implementation Roadmap")
            for i, step in enumerate(roadmap.get("implementation_steps", []), 1):
                clean_step = str(step).lstrip("0123456789. ")
                st.markdown(f"""
                <div class="step-card">
                    <span class="step-title">Phase {i}:</span> {clean_step}
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🔍 Risk Assessment, Validation & Deliverables", expanded=True):
                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    st.markdown("**⚠️ Anticipated Technical Challenges:**")
                    for ec in roadmap.get("expected_challenges", []):
                        st.markdown(f"- {ec}")
                        
                    st.markdown("**✅ Validation & Verification Steps:**")
                    for vs in roadmap.get("validation_steps", []):
                        st.markdown(f"- {vs}")
                        
                with v_col2:
                    st.markdown("**🏆 Target Research Outcomes:**")
                    for eo in roadmap.get("expected_outcomes", []):
                        st.markdown(f"- {eo}")
                        
                    st.markdown(f"**⏱️ Total Timeline:** `{roadmap.get('timeline_weeks', 4)} Weeks`")
        else:
            st.warning("No roadmap synthesized.")

    # -----------------------------------------------------------------------
    # TAB 2: Research Gaps & Critic Evaluation
    # -----------------------------------------------------------------------
    with tab_gaps:
        gaps = data.get("gaps", [])
        critic_results = data.get("critic_results", [])
        
        st.subheader(f"🔎 Discovered Research Gaps ({len(gaps)}) & 🧑‍🏫 Mentor Critic Reviews")
        st.caption("Gaps are identified across literature and independently peer-evaluated by the skeptical Critic Agent.")
        
        if gaps:
            for i, gap_item in enumerate(gaps):
                conf = str(gap_item.get("confidence", "Medium")).strip().capitalize()
                badge_color = "🟢" if conf == "High" else ("🟡" if conf == "Medium" else "🔴")
                gap_type = gap_item.get("gap_type", "General Gap")
                gap_text = gap_item.get("gap", "Unnamed Gap")
                
                # Matching Critic Result
                critic_info = critic_results[i] if i < len(critic_results) else {}
                verdict = critic_info.get("verdict", "Evaluated")
                v_icon = "✅" if "Supported" in verdict and "Partially" not in verdict and "Weak" not in verdict else ("⚠️" if "Partially" in verdict else "❌")
                
                with st.expander(f"🔬 Gap #{i+1}: {gap_text} | {v_icon} Verdict: {verdict}", expanded=(i==0)):
                    g_col1, g_col2 = st.columns([1.2, 1])
                    
                    with g_col1:
                        st.markdown(f"**🏷️ Gap Type:** `{gap_type}` | **Confidence:** {badge_color} {conf}")
                        st.markdown(f"**📌 Formulated Gap:**\n{gap_text}")
                        st.markdown(f"**🧾 Literature Evidence:**\n{gap_item.get('evidence', 'N/A')}")
                        
                        papers_list = gap_item.get("supporting_papers", [])
                        if papers_list:
                            st.markdown("**📚 Supporting Papers:** " + ", ".join(f"`{p}`" for p in papers_list))
                        st.markdown(f"**💡 Research Opportunity:**\n{gap_item.get('research_opportunity', 'N/A')}")

                    with g_col2:
                        st.markdown("##### 🧑‍🏫 Mentor Critic Evaluation")
                        st.markdown(f"**Verdict:** {v_icon} **{verdict}**")
                        st.markdown(f"**Evidence Strength:** `{critic_info.get('evidence_strength', 'Medium')}`")
                        st.markdown(f"**Reasoning:**\n{critic_info.get('reasoning', 'N/A')}")
                        st.markdown(f"**Concerns:**\n{critic_info.get('concerns', 'N/A')}")
                        st.markdown(f"**Recommendation:**\n{critic_info.get('recommendation', 'N/A')}")
        else:
            st.info("No explicit cross-paper gaps were detected in this literature sample.")

    # -----------------------------------------------------------------------
    # TAB 3: RAG Deep Paper Analysis
    # -----------------------------------------------------------------------
    with tab_analysis:
        analysis_results = data.get("analysis_results", [])
        st.subheader(f"📊 RAG-Grounded Paper Analysis ({len(analysis_results)})")
        st.caption("Extracted using vector embeddings (FAISS + sentence-transformers) grounded strictly in retrieved chunks.")
        
        if analysis_results:
            for i, analysis in enumerate(analysis_results, 1):
                paper_title = analysis.get("title") or f"Paper #{i}"
                with st.expander(f"📑 {i}. {paper_title}", expanded=(i <= 2)):
                    a_col1, a_col2 = st.columns(2)
                    with a_col1:
                        st.markdown(f"**🎯 Research Problem:**\n{analysis.get('research_problem', 'N/A')}")
                        st.markdown(f"**⚙️ Methodology:**\n{analysis.get('methodology', 'N/A')}")
                        st.markdown(f"**💾 Datasets Used:**\n{analysis.get('datasets', 'N/A')}")

                    with a_col2:
                        st.markdown(f"**⚠️ Stated Limitations:**\n{analysis.get('limitations', 'N/A')}")
                        st.markdown(f"**🚀 Proposed Future Work:**\n{analysis.get('future_work', 'N/A')}")

                    findings = analysis.get("key_findings", [])
                    st.markdown("**🔍 Key Findings:**")
                    if isinstance(findings, list) and findings:
                        for item in findings:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(str(findings) if findings else "Not specified.")

                    evidence_sources = analysis.get("evidence_sources", [])
                    if evidence_sources:
                        st.markdown("---")
                        st.markdown(f"📚 **RAG Evidence Chunks Used ({len(evidence_sources)})**")
                        for chunk in evidence_sources[:3]:
                            chunk_text = chunk.get("text", "")[:200] + "..."
                            st.caption(f"Snippet: \"{chunk_text}\"")

    # -----------------------------------------------------------------------
    # TAB 4: Literature Discovery
    # -----------------------------------------------------------------------
    with tab_papers:
        papers = data.get("papers", [])
        st.subheader(f"📄 Discovered Literature ({len(papers)})")
        
        if papers:
            # Simple Source Filter
            sources = list(set(p.get("source", "unknown") for p in papers))
            selected_src = st.multiselect("Filter by Source Database:", sources, default=sources)
            
            filtered_papers = [p for p in papers if p.get("source", "unknown") in selected_src]
            
            for i, paper in enumerate(filtered_papers, 1):
                title = paper.get("title", "Untitled")
                source = paper.get("source", "unknown")
                year = paper.get("year")
                citations = paper.get("citation_count")
                venue = paper.get("venue")
                url = paper.get("url")
                
                src_badge = "🔵 Semantic Scholar" if source == "semantic_scholar" else ("🟠 arXiv" if source == "arxiv" else "🟢 Synthesized")
                year_str = f"({year})" if year else ""
                
                st.markdown(f"#### {i}. {title} {year_str}")
                st.markdown(f"`Source: {src_badge}` | `Venue: {venue or 'Academic'}`" + (f" | `Citations: {citations}`" if citations is not None else ""))
                
                authors = paper.get("authors", [])
                if authors:
                    st.caption(f"Authors: {', '.join(authors[:5])}")
                    
                if url:
                    st.markdown(f"🔗 [View Full Paper Link]({url})")
                    
                abstract = paper.get("abstract")
                if abstract:
                    with st.expander("Read Abstract"):
                        st.write(abstract)
                st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # TAB 5: Research Plan & Strategy
    # -----------------------------------------------------------------------
    with tab_plan:
        planner_output = data.get("planner_output", {})
        st.subheader("📋 Planner Agent Output")
        
        if planner_output:
            st.markdown(f"### {planner_output.get('title', 'Research Plan')}")
            st.write(planner_output.get("summary", ""))
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown("**🏷️ Keywords:** " + ", ".join(f"`{k}`" for k in planner_output.get("keywords", [])))
                st.markdown("**📌 Subtopics:**")
                for sub in planner_output.get("subtopics", []):
                    st.markdown(f"- {sub}")

            with p_col2:
                st.markdown("**❓ Proposed Questions:**")
                for q in planner_output.get("research_questions", []):
                    st.markdown(f"- {q}")
                    
                st.markdown("**🔬 Methodology Suggestions:**")
                for m in planner_output.get("methodology_suggestions", []):
                    st.markdown(f"- {m}")
                    
    # -----------------------------------------------------------------------
    # Export Report Dossier
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📥 Export Full Research Dossier")
    
    dossier_json = json.dumps(data, indent=2)
    dossier_md = f"# ReSearchAI Dossier: {topic_name}\n\n"
    dossier_md += f"## Research Direction\n{data.get('roadmap', {}).get('research_direction', 'N/A')}\n\n"
    dossier_md += f"## Objective\n{data.get('roadmap', {}).get('objective', 'N/A')}\n\n"
    dossier_md += "## Discovered Papers\n"
    for p in data.get("papers", []):
        dossier_md += f"- **{p.get('title')}** ({p.get('year')}) - {p.get('url', 'N/A')}\n"
        
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.download_button(
            label="📄 Download Markdown Dossier (.md)",
            data=dossier_md,
            file_name=f"research_dossier_{topic_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )
    with exp_col2:
        st.download_button(
            label="💾 Download Full JSON Data (.json)",
            data=dossier_json,
            file_name=f"research_data_{topic_name.replace(' ', '_')}.json",
            mime="application/json"
        )
