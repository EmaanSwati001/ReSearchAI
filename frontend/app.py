# frontend/app.py

"""ReSearchAI - Autonomous AI Research Mentor & Capstone Studio.

Modern, multi-agent Streamlit interface featuring:
- Editorial SaaS Landing Page & Research Studio
- Interactive Topic Inspiration Presets
- Live Multi-Agent Pipeline Progress Visualizer
- Prominent Discovered Literature Dossier (Papers, Links, Abstracts, Citations)
- Phased Milestone Roadmap, RAG Deep Extraction, and Adversarial Peer Critic
- Full Dossier Export (Markdown & JSON)
"""

import streamlit as st
import requests
import json
import time
import os
import concurrent.futures
from typing import Dict, Any

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ReSearchAI | Autonomous Research Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# Custom CSS Design System (High Contrast, Professional Studio Theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Reset & Clean Dark Foundation */
    header[data-testid="stHeader"], .stAppHeader {
        background-color: #080d1a !important;
        color: #f8fafc !important;
    }
    
    .stApp, div[data-testid="stToolbar"] {
        background-color: #080d1a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Typography & Contrast */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp li, .stApp label, .stMarkdown, .stMarkdown p {
        color: #f1f5f9 !important;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Brand Accent Highlights */
    .accent-text {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Top Brand Navigation Bar */
    .brand-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 0 1.5rem 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 2rem;
    }
    .brand-logo {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff !important;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .brand-badge {
        background: #1e293b;
        color: #38bdf8 !important;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #334155;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1.5rem 2rem 1.5rem;
        max-width: 900px;
        margin: 0 auto;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.2;
        color: #ffffff !important;
        margin-bottom: 1.2rem;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        line-height: 1.6;
        color: #94a3b8 !important;
        margin-bottom: 2rem;
    }

    /* Search Studio Console Card */
    .search-console {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
        margin-bottom: 2.5rem;
    }

    /* Feature Grid Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.2rem;
        margin-top: 1.5rem;
        margin-bottom: 3rem;
    }
    .feature-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.4rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.88rem;
        color: #94a3b8 !important;
        line-height: 1.5;
    }

    /* Literature & Paper Display Cards */
    .paper-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.6rem;
        margin-bottom: 1.2rem;
        transition: border-color 0.2s ease;
    }
    .paper-card:hover {
        border-color: #38bdf8;
    }
    .paper-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    .paper-meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .pill-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .pill-arxiv { background: rgba(249, 115, 22, 0.15); color: #fb923c !important; border: 1px solid rgba(249, 115, 22, 0.3); }
    .pill-s2 { background: rgba(14, 165, 233, 0.15); color: #38bdf8 !important; border: 1px solid rgba(14, 165, 233, 0.3); }
    .pill-synth { background: rgba(34, 197, 94, 0.15); color: #4ade80 !important; border: 1px solid rgba(34, 197, 94, 0.3); }
    .pill-metric { background: #1e293b; color: #cbd5e1 !important; border: 1px solid #334155; }
    
    .paper-authors {
        font-size: 0.88rem;
        color: #94a3b8 !important;
        margin-bottom: 0.8rem;
    }
    .paper-abstract-box {
        background: #090d16;
        border-left: 3px solid #38bdf8;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.6rem;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #cbd5e1 !important;
    }

    /* Metric Summary Strip */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 768px) {
        .kpi-container { grid-template-columns: repeat(2, 1fr); }
    }
    .kpi-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8 !important;
        line-height: 1;
        margin-bottom: 0.4rem;
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Roadmap Phase Cards */
    .phase-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .phase-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #38bdf8 !important;
        margin-bottom: 0.4rem;
    }
    .phase-desc {
        color: #e2e8f0 !important;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Streamlit Components Overrides */
    div[data-testid="stExpander"] {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
    }
    div[data-testid="stExpander"] * {
        color: #f8fafc !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0f172a !important;
        border: 1px solid #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.4rem !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease;
    }
    .stButton > button *, .stDownloadButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        border-color: #7dd3fc !important;
        transform: translateY(-1px);
    }

    /* Secondary Preset Buttons */
    button[kind="secondary"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #cbd5e1 !important;
    }
    button[kind="secondary"]:hover {
        background: #334155 !important;
        color: #ffffff !important;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #090d16 !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input:focus {
        border-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "query_topic" not in st.session_state:
    st.session_state["query_topic"] = "AI-driven Early Disease Diagnosis & Medical Imaging"
if "query_experience" not in st.session_state:
    st.session_state["query_experience"] = "beginner"
if "query_interest" not in st.session_state:
    st.session_state["query_interest"] = ""

# ---------------------------------------------------------------------------
# Top Brand Navigation
# ---------------------------------------------------------------------------
st.markdown("""
<div class="brand-navbar">
    <div class="brand-logo">
        <span>🎓 ReSearchAI</span>
        <span class="brand-badge">Autonomous Multi-Agent Studio</span>
    </div>
    <div style="display:flex; gap:1rem; align-items:center;">
        <span style="font-size:0.85rem; color:#94a3b8;">LangGraph Orchestrated · 7 Autonomous Agents</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# LANDING VIEW / INPUT CONSOLE (When not displaying active results)
# ---------------------------------------------------------------------------
results_ready = "research_data" in st.session_state

if not results_ready:
    # Editorial Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-tag">⚡ Autonomous Research Intelligence & Synthesis</div>
        <div class="hero-title">From Broad Inquiries to <span class="accent-text">Peer-Reviewed Evidence</span> and Actionable Roadmaps</div>
        <div class="hero-subtitle">ReSearchAI coordinates a 7-agent pipeline to harvest academic literature from arXiv & Semantic Scholar, extract vector RAG insights, detect cross-paper research gaps, stress-test claims with an adversarial critic, and build your execution roadmap.</div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Topic Inspiration Chips (Quick Presets)
    st.markdown("##### 💡 Explore Curated Research Presets")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    with col_p1:
        if st.button("🧬 AI in Healthcare Diagnosis", use_container_width=True):
            st.session_state["query_topic"] = "AI-driven Early Disease Diagnosis & Medical Imaging"
            st.session_state["query_experience"] = "intermediate"
            st.session_state["query_interest"] = "Vision Transformers in Oncology"
            st.rerun()
            
    with col_p2:
        if st.button("🛡️ LLM Hallucination Mitigation", use_container_width=True):
            st.session_state["query_topic"] = "Mitigating Hallucinations in LLMs via Retrieval-Augmented Generation"
            st.session_state["query_experience"] = "intermediate"
            st.session_state["query_interest"] = "Self-Reflective RAG"
            st.rerun()
            
    with col_p3:
        if st.button("⚛️ Quantum Machine Learning", use_container_width=True):
            st.session_state["query_topic"] = "Quantum Machine Learning Algorithms for Drug Discovery"
            st.session_state["query_experience"] = "expert"
            st.session_state["query_interest"] = "Variational Quantum Eigensolvers"
            st.rerun()
            
    with col_p4:
        if st.button("🤖 Autonomous Swarm Robotics", use_container_width=True):
            st.session_state["query_topic"] = "Autonomous Navigation & Consensus in Robot Swarms"
            st.session_state["query_experience"] = "beginner"
            st.session_state["query_interest"] = "Decentralized SLAM"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Search & Execution Console Card
    st.markdown("##### 🔬 Launch Research Investigation")
    with st.container():
        c1, c2, c3 = st.columns([3, 1.2, 1.8])
        with c1:
            in_topic = st.text_input(
                "Research Topic or Hypothesis",
                value=st.session_state["query_topic"],
                placeholder="e.g. Self-Supervised Learning for Protein Folding",
                help="Enter any scientific domain, hypothesis, or research problem."
            )
        with c2:
            levels = ["beginner", "intermediate", "expert"]
            curr_idx = levels.index(st.session_state["query_experience"]) if st.session_state["query_experience"] in levels else 0
            in_level = st.selectbox(
                "Target Skill Level",
                levels,
                index=curr_idx,
                help="Calibrates the depth, methodology, and recommendations."
            )
        with c3:
            in_focus = st.text_input(
                "Specific Focus / Constraint (Optional)",
                value=st.session_state["query_interest"],
                placeholder="e.g. Low-resource edge devices"
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        launch_btn = st.button("🚀 Synthesize Research Intelligence →", type="primary", use_container_width=True)

    # Trigger Pipeline Execution
    if launch_btn:
        if not in_topic.strip():
            st.warning("⚠️ Please provide a research topic to begin.")
        else:
            payload = {
                "topic": in_topic.strip(),
                "experience_level": in_level,
                "interest": in_focus.strip() if in_focus.strip() else None,
            }
            
            status_container = st.empty()
            progress_container = st.progress(10)
            
            stages = [
                (20, "🧠 **Planner Agent:** Formulating multi-faceted research hypotheses and search strategy..."),
                (40, "🔍 **Discovery Agent:** Ingesting academic literature from arXiv & Semantic Scholar databases..."),
                (60, "📚 **Vector RAG Engine:** Embedding document chunks into FAISS vector space for grounded retrieval..."),
                (75, "📊 **Analysis Agent:** Extracting empirical methodologies, benchmarks, and dataset constraints..."),
                (88, "🔎 **Gap Analysis Agent:** Discovering cross-paper research opportunities and unexplored frontiers..."),
                (96, "🧑‍🏫 **Critic & Roadmap Agents:** Stress-testing peer evidence and building execution milestones...")
            ]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(requests.post, f"{BACKEND_URL}/research", json=payload, timeout=300)
                stage_idx = 0
                start_time = time.time()
                
                while not future.done():
                    pct, msg = stages[min(stage_idx, len(stages) - 1)]
                    elapsed = int(time.time() - start_time)
                    status_container.info(f"{msg} *(Elapsed: {elapsed}s)*")
                    progress_container.progress(pct)
                    time.sleep(3.0)
                    if stage_idx < len(stages) - 1:
                        stage_idx += 1
                        
                try:
                    response = future.result()
                    response.raise_for_status()
                    result_data = response.json()
                    
                    progress_container.progress(100)
                    status_container.success("✅ Research synthesis completed successfully! Loading workspace...")
                    time.sleep(0.6)
                    status_container.empty()
                    progress_container.empty()
                    
                    st.session_state["research_data"] = result_data
                    st.session_state["research_topic"] = in_topic.strip()
                    st.rerun()
                except Exception as e:
                    progress_container.empty()
                    status_container.error(f"❌ Pipeline Execution Error: {e}")

    # Feature Value Pillars
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Dual Academic Discovery</div>
            <div class="feature-desc">Simultaneous automated querying across Semantic Scholar and arXiv, ranking top peer-reviewed literature with full citation metrics and direct DOI links.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Grounded Vector RAG</div>
            <div class="feature-desc">FAISS vector store and sentence-transformers chunking guarantees all extracted methods, datasets, and limitations are cited directly from source text.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧑‍🏫</div>
            <div class="feature-title">Adversarial Peer Critic</div>
            <div class="feature-desc">A skeptical reviewer agent stress-tests every identified research gap, categorizing claims into Supported, Partially Supported, or Rejected with rigorous reasoning.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Milestone Execution Plan</div>
            <div class="feature-desc">Transforms academic insights into a calibrated multi-week student roadmap featuring core objectives, implementation phases, and evaluation metrics.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Architecture Overview Expander
    with st.expander("🛠️ System Architecture & Multi-Agent Orchestration Flow"):
        st.markdown("""
        ```mermaid
        graph TD
            User([User Research Topic]) --> Planner[1. Planner Agent]
            Planner --> Discovery[2. Literature Discovery]
            Discovery -->|arXiv & Semantic Scholar| RAG[3. Vector RAG Engine]
            RAG -->|FAISS Chunks| Analysis[4. Paper Analysis]
            Analysis --> Gap[5. Gap Analysis Agent]
            Gap --> Critic[6. Research Critic Agent]
            Critic --> Roadmap[7. Roadmap Generator]
            Roadmap --> Dossier([Executive Research Dossier])
        ```
        - **LangGraph State Graph**: Cyclic feedback and typed state preservation across all 7 reasoning agents.
        - **Model Support**: Groq High-Speed Inference (`qwen/qwen3.8-27b`) with automatic fallback to Gemini & OpenAI.
        - **Vector Store**: In-memory FAISS indexing with `all-MiniLM-L6-v2` dense embeddings.
        """)

# ---------------------------------------------------------------------------
# RESULTS WORKSPACE (When research data is present in session)
# ---------------------------------------------------------------------------
else:
    data = st.session_state["research_data"]
    topic_name = st.session_state.get("research_topic", "Research Topic")
    
    # Header Bar with "New Query" and "Export" Actions
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f"## 🔬 Research Dossier: <span class='accent-text'>{topic_name}</span>", unsafe_allow_html=True)
        st.caption("Multi-Agent Autonomous Synthesis · Grounded in Academic Literature & Adversarial Peer Review")
    with h_col2:
        st.markdown("<div style='text-align: right; padding-top: 0.5rem;'>", unsafe_allow_html=True)
        if st.button("← New Research Query", use_container_width=True):
            del st.session_state["research_data"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Executive KPI Metric Bar
    papers = data.get("papers", [])
    analysis_results = data.get("analysis_results", [])
    gaps = data.get("gaps", [])
    critic_results = data.get("critic_results", [])
    roadmap = data.get("roadmap", {})
    timeline_weeks = roadmap.get("timeline_weeks", "4")

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-box">
            <div class="kpi-value">{len(papers)}</div>
            <div class="kpi-label">Papers Discovered</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{len(analysis_results)}</div>
            <div class="kpi-label">RAG Synthesized</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{len(gaps)}</div>
            <div class="kpi-label">Research Gaps</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{len(critic_results)}</div>
            <div class="kpi-label">Critic Reviews</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{timeline_weeks}w</div>
            <div class="kpi-label">Execution Timeline</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Workspace Tabbed Experience (Papers front and center as requested)
    tab_papers, tab_roadmap, tab_gaps, tab_analysis, tab_strategy = st.tabs([
        "📄 Discovered Literature & Evidence",
        "🗺️ Actionable Research Roadmap",
        "🔎 Research Gaps & Peer Critic",
        "📊 Deep RAG Extraction",
        "📋 Research Strategy & Plan"
    ])

    # -----------------------------------------------------------------------
    # TAB 1: Literature Discovery & Direct Links & Full Abstracts
    # -----------------------------------------------------------------------
    with tab_papers:
        st.markdown(f"### 📄 Discovered Research Literature ({len(papers)} Papers)")
        st.caption("Live academic records retrieved from Semantic Scholar and arXiv, ranked and indexed for vector grounding.")
        
        if papers:
            for i, p in enumerate(papers, 1):
                title = p.get("title", "Untitled Paper")
                source = p.get("source", "unknown")
                year = p.get("year")
                citations = p.get("citation_count")
                venue = p.get("venue")
                url = p.get("url")
                authors = p.get("authors", [])
                abstract = p.get("abstract", "")
                
                # Badges
                if source == "arxiv":
                    src_badge = '<span class="pill-badge pill-arxiv">🟠 arXiv</span>'
                elif source == "semantic_scholar":
                    src_badge = '<span class="pill-badge pill-s2">🔵 Semantic Scholar</span>'
                else:
                    src_badge = '<span class="pill-badge pill-synth">🟢 Synthesized Literature</span>'
                    
                meta_html = f"{src_badge}"
                if year:
                    meta_html += f' <span class="pill-badge pill-metric">📅 {year}</span>'
                if citations is not None:
                    meta_html += f' <span class="pill-badge pill-metric">⭐ {citations} citations</span>'
                if venue:
                    meta_html += f' <span class="pill-badge pill-metric">🏛️ {venue}</span>'

                author_str = ", ".join(authors[:5]) if authors else "Author list in publication"
                
                link_html = f'<a href="{url}" target="_blank" style="color:#38bdf8; text-decoration:none; font-weight:600;">🔗 View Full Paper on Source Database →</a>' if url else '<span style="color:#64748b;">Direct link unavailable</span>'

                abstract_content = abstract if abstract else "Abstract text was not returned by the database API for this specific index record."

                st.markdown(f"""
                <div class="paper-card">
                    <div class="paper-title">{i}. {title}</div>
                    <div class="paper-meta-row">{meta_html}</div>
                    <div class="paper-authors"><strong>Authors:</strong> {author_str}</div>
                    <div style="margin-bottom: 0.8rem;">{link_html}</div>
                    <div class="paper-abstract-box">
                        <strong>Abstract:</strong><br>{abstract_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No literature was discovered for this topic inquiry.")

    # -----------------------------------------------------------------------
    # TAB 2: Actionable Roadmap & Milestones
    # -----------------------------------------------------------------------
    with tab_roadmap:
        if roadmap:
            direction = roadmap.get('research_direction', 'Targeted Literature Benchmarking & Empirical Evaluation')
            if "Pending further validation" in direction or direction == "N/A":
                direction = f"Targeted Literature Benchmarking & Empirical Evaluation in {topic_name}"
                
            objective = roadmap.get('objective', f'Evaluate baseline architectures and establish empirical validation for {topic_name}.')
            if "Establish a valid research objective" in objective or objective == "N/A":
                objective = f"Establish rigorous benchmark evaluation, test foundational baselines, and resolve domain generalization bottlenecks for {topic_name}."

            st.markdown(f"### 🗺️ Actionable Research Roadmap")
            
            # Direction & Objective Callout
            st.markdown(f"""
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:1.4rem; margin-bottom:1.5rem;">
                <div style="font-size:1.05rem; font-weight:700; color:#38bdf8; margin-bottom:0.4rem;">🎯 Strategic Objective</div>
                <div style="color:#f8fafc; font-size:1rem; line-height:1.5; margin-bottom:1rem;">{objective}</div>
                <div style="font-size:0.95rem; font-weight:700; color:#38bdf8; margin-bottom:0.4rem;">📌 Core Research Direction</div>
                <div style="color:#cbd5e1; font-size:0.95rem; line-height:1.5;">{direction}</div>
            </div>
            """, unsafe_allow_html=True)

            r1, r2 = st.columns(2)
            with r1:
                st.markdown("#### ❓ Central Research Questions")
                for rq in roadmap.get("research_questions", []):
                    st.markdown(f"- 🔹 **{rq}**")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### ⚙️ Technical Methodology")
                for m in roadmap.get("methodology", []):
                    clean_m = str(m).lstrip("0123456789. ")
                    st.markdown(f"- 🔬 {clean_m}")

            with r2:
                st.markdown("#### 💾 Required Datasets & Compute")
                for dr in roadmap.get("data_requirements", []):
                    st.markdown(f"- 📊 {dr}")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📈 Benchmark & Evaluation Metrics")
                for em in roadmap.get("evaluation_metrics", []):
                    st.markdown(f"- 🎯 {em}")

            st.markdown("---")
            st.markdown("#### 🚀 Phased Implementation Steps")
            steps = roadmap.get("implementation_steps", [])
            for i, step in enumerate(steps, 1):
                clean_step = str(step).lstrip("0123456789. ")
                st.markdown(f"""
                <div class="phase-card">
                    <div class="phase-title">Phase {i}</div>
                    <div class="phase-desc">{clean_step}</div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("⚠️ Anticipated Technical Challenges & Mitigation Strategy"):
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.markdown("**Anticipated Pitfalls:**")
                    for ch in roadmap.get("expected_challenges", []):
                        st.markdown(f"- ⚠️ {ch}")
                with c_col2:
                    st.markdown("**Validation Checkpoints:**")
                    for val in roadmap.get("validation_steps", []):
                        st.markdown(f"- ✅ {val}")
        else:
            st.warning("No roadmap synthesized.")

    # -----------------------------------------------------------------------
    # TAB 3: Gaps & Adversarial Peer Critic
    # -----------------------------------------------------------------------
    with tab_gaps:
        st.markdown(f"### 🔎 Research Gaps & Adversarial Peer Critic Reviews ({len(gaps)})")
        st.caption("Hypotheses identified by the Gap Analysis Agent and independently stress-tested by the Critic Agent.")
        
        if gaps:
            for i, g in enumerate(gaps):
                conf = str(g.get("confidence", "Medium")).strip().capitalize()
                gap_type = g.get("gap_type", "Literature Gap")
                gap_text = g.get("gap", "Formulated Gap")
                
                critic_info = critic_results[i] if i < len(critic_results) else {}
                verdict = critic_info.get("verdict", "Evaluated")
                
                if "Supported" in verdict and "Partially" not in verdict and "Weak" not in verdict:
                    verdict_badge = '<span class="pill-badge" style="background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.3);">✅ Supported</span>'
                elif "Partially" in verdict:
                    verdict_badge = '<span class="pill-badge" style="background:rgba(234,179,8,0.15); color:#facc15; border:1px solid rgba(234,179,8,0.3);">⚠️ Partially Supported</span>'
                else:
                    verdict_badge = '<span class="pill-badge" style="background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.3);">❌ Skeptical / Rejected</span>'

                with st.expander(f"🔬 Gap #{i+1}: {gap_text[:90]}...", expanded=(i == 0)):
                    col_g1, col_g2 = st.columns([1.2, 1])
                    with col_g1:
                        st.markdown(f"**Category:** `{gap_type}` | **Agent Confidence:** `{conf}`")
                        st.markdown(f"**📌 Discovered Gap:**\n{gap_text}")
                        st.markdown(f"**🧾 Literature Evidence:**\n{g.get('evidence', 'Extracted from cross-paper corpus.')}")
                        
                        supporting = g.get("supporting_papers", [])
                        if supporting:
                            st.markdown(f"**📚 Supporting Papers:** {', '.join(f'`{p}`' for p in supporting)}")
                            
                        st.markdown(f"**💡 High-Impact Opportunity:**\n{g.get('research_opportunity', 'Novel empirical exploration.')}")

                    with col_g2:
                        st.markdown("##### 🧑‍🏫 Critic Peer Review")
                        st.markdown(f"**Verdict:** {verdict_badge}", unsafe_allow_html=True)
                        st.markdown(f"**Evidence Grounding:** `{critic_info.get('evidence_strength', 'Evaluated')}`")
                        st.markdown(f"**Reviewer Reasoning:**\n{critic_info.get('reasoning', 'Evidence holds for current baseline studies.')}")
                        st.markdown(f"**Concerns / Caveats:**\n{critic_info.get('concerns', 'Requires careful benchmarking against newer baselines.')}")
                        st.markdown(f"**Recommendation:**\n{critic_info.get('recommendation', 'Proceed with targeted baseline validation.')}")
        else:
            st.info("No explicit cross-paper gaps were detected.")

    # -----------------------------------------------------------------------
    # TAB 4: Deep RAG Extraction
    # -----------------------------------------------------------------------
    with tab_analysis:
        st.markdown(f"### 📊 RAG-Grounded Paper Analysis ({len(analysis_results)})")
        st.caption("Extracted using dense FAISS vector retrieval grounded strictly in retrieved academic chunks.")
        
        if analysis_results:
            for i, an in enumerate(analysis_results, 1):
                p_title = an.get("title") or f"Paper #{i}"
                with st.expander(f"📑 {i}. {p_title}", expanded=(i <= 2)):
                    c_a1, c_a2 = st.columns(2)
                    with c_a1:
                        st.markdown(f"**🎯 Research Problem:**\n{an.get('research_problem', 'N/A')}")
                        st.markdown(f"**⚙️ Methodology:**\n{an.get('methodology', 'N/A')}")
                        st.markdown(f"**💾 Datasets Used:**\n{an.get('datasets', 'N/A')}")
                    with c_a2:
                        st.markdown(f"**⚠️ Limitations:**\n{an.get('limitations', 'N/A')}")
                        st.markdown(f"**🚀 Proposed Future Work:**\n{an.get('future_work', 'N/A')}")
                        
                    findings = an.get("key_findings", [])
                    st.markdown("**🔍 Key Findings:**")
                    if isinstance(findings, list) and findings:
                        for kf in findings:
                            st.markdown(f"- {kf}")
                    else:
                        st.markdown(str(findings) if findings else "Not specified.")
                        
                    ev = an.get("evidence_sources", [])
                    if ev:
                        st.markdown("---")
                        st.markdown(f"📚 **Vector Evidence Snippets ({len(ev)})**")
                        for chunk in ev[:3]:
                            st.caption(f"\"{chunk.get('text', '')[:220]}...\"")
        else:
            st.info("No deep RAG analyses recorded.")

    # -----------------------------------------------------------------------
    # TAB 5: Research Strategy & Plan
    # -----------------------------------------------------------------------
    with tab_strategy:
        planner_data = data.get("planner_output", {})
        st.markdown("### 📋 Planner Agent Strategy & Decomposition")
        if planner_data:
            st.markdown(f"#### {planner_data.get('title', 'Initial Research Blueprint')}")
            st.write(planner_data.get("summary", ""))
            
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("**🏷️ Search Keywords:**")
                st.write(", ".join(f"`{k}`" for k in planner_data.get("keywords", [])))
                st.markdown("**📌 Key Subtopics:**")
                for sub in planner_data.get("subtopics", []):
                    st.markdown(f"- {sub}")
            with p2:
                st.markdown("**❓ Proposed Inquiries:**")
                for q in planner_data.get("research_questions", []):
                    st.markdown(f"- {q}")
                st.markdown("**🔬 Suggested Methodologies:**")
                for m in planner_data.get("methodology_suggestions", []):
                    st.markdown(f"- {m}")
        else:
            st.info("Planner data not available.")

    # -----------------------------------------------------------------------
    # Export Actions
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📥 Export Executive Dossier")
    
    dossier_json = json.dumps(data, indent=2)
    dossier_md = f"# ReSearchAI Dossier: {topic_name}\n\n"
    dossier_md += f"## Strategic Objective\n{roadmap.get('objective', 'N/A')}\n\n"
    dossier_md += f"## Research Direction\n{roadmap.get('research_direction', 'N/A')}\n\n"
    dossier_md += "## Discovered Literature\n"
    for p in papers:
        dossier_md += f"- **{p.get('title')}** ({p.get('year')}) [{p.get('source')}]: {p.get('url', 'N/A')}\n"
        if p.get('abstract'):
            dossier_md += f"  > {p.get('abstract')}\n"
    dossier_md += "\n## Synthesized Gaps & Critic Reviews\n"
    for i, g in enumerate(gaps):
        c_item = critic_results[i] if i < len(critic_results) else {}
        dossier_md += f"### Gap {i+1}: {g.get('gap')}\n- **Type:** {g.get('gap_type')}\n- **Critic Verdict:** {c_item.get('verdict')}\n- **Reasoning:** {c_item.get('reasoning')}\n\n"

    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button(
            "📄 Download Markdown Dossier (.md)",
            data=dossier_md,
            file_name=f"research_dossier_{topic_name.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with ex2:
        st.download_button(
            "💾 Download Complete JSON (.json)",
            data=dossier_json,
            file_name=f"research_data_{topic_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
