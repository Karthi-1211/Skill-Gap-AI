import streamlit as st
import time
import textwrap
import pandas as pd
import numpy as np
from collections import Counter
# Imports moved inside functions to save memory


try:
    from milestone2 import extract_skills as extract_skills_m1, SKILL_CATEGORIES, get_skill_category
except ImportError:
    # Fallback if M2 shouldn't crash M3 independently
    extract_skills_m1 = lambda x: []
    SKILL_CATEGORIES = {}
    def get_skill_category(s): return "General"

@st.cache_resource(show_spinner="Loading AI Neural Network...")
def load_model():
    # Model is loaded once per session
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data(show_spinner="Analyzing Semantic Similarity...")
def compute_similarity(resume_skills, jd_skills, match_thr=0.8, partial_thr=0.5):
    """
    Computes semantic similarity between resume and JD skills using vector embeddings.
    Optimized for Streamlit caching.
    """
    if not resume_skills or not jd_skills:
        return pd.DataFrame(), [], {"overall": 0, "matched": 0, "partial": 0, "missing": 0, "total": 0}

    from sklearn.metrics.pairwise import cosine_similarity
    model = load_model()
    
    all_text = resume_skills + jd_skills
    embeddings = model.encode(all_text, normalize_embeddings=True)
    
    # Split embeddings back
    n_res = len(resume_skills)
    res_emb = embeddings[:n_res]
    jd_emb = embeddings[n_res:]
    
    sim_matrix = cosine_similarity(jd_emb, res_emb)
    
    jd_details = []
    plot_data = []
    
    matched_count = 0
    partial_count = 0
    missing_count = 0
    
    for i, jd_skill in enumerate(jd_skills):
        row = sim_matrix[i]
        best_idx = np.argmax(row)
        best_match_skill = resume_skills[best_idx]
        score = float(row[best_idx])
        
        if score >= match_thr:
            category = "High Match"
            matched_count += 1
        elif score >= partial_thr:
            category = "Partial Match"
            partial_count += 1
        else:
            category = "Low Match"
            missing_count += 1
            
        jd_details.append({
            "jd_skill": jd_skill,
            "resume_match": best_match_skill,
            "score": score,
            "category": category
        })
        
        for j, res_skill in enumerate(resume_skills):
            
            if jd_skill.lower().strip() == res_skill.lower().strip():
                s_val = 1.0
            else:
                s_val = float(sim_matrix[i][j])
            
            # Optimization: Only add relevant points to the plot to keep UI snappy
            if s_val > 0.3: 
                cat = "High Match" if s_val >= match_thr else "Partial Match" if s_val >= partial_thr else "Low Match"
                plot_data.append({
                    "jd_skill": jd_skill,
                    "resume_skill": res_skill,
                    "score": s_val,
                    "category": cat
                })

    total = len(jd_skills)
    overall_score = int(((matched_count * 1.0) + (partial_count * 0.5)) / total * 100) if total > 0 else 0
    
    stats = {
        "overall": overall_score,
        "matched": matched_count,
        "partial": partial_count,
        "missing": missing_count,
        "total": total
    }
    
    return pd.DataFrame(plot_data), jd_details, stats

def app():
    import components
    import charts
    from components import navigate_to


    # ====================== PREMIUM CSS INJECTION ======================
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background: #0f172a;
        color: #e2e8f0;
    }

    .main > div {
        padding-top: 2rem;
    }

    /* Floating Glass Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        /* Deeper, richer background */
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(30, 41, 59, 0.85)) !important;
        
        /* Glassmorphism */
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        
        /* Border with a subtle gradient hint */
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
        
        border-radius: 24px !important;
        
        /* Enhanced Shadow */
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.3), 
            0 10px 30px -5px rgba(0, 0, 0, 0.5),
            inset 0 0 20px rgba(255, 255, 255, 0.02) !important;
            
        padding: 24px !important;
        transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        position: relative;
        z-index: 1;
        overflow: hidden !important;
    }

    /* Internal Texture/Shimmer Effect via ::after */
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        /* Increased opacity values for visibility */
        background: 
            radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.1) 0%, transparent 60%),
            linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%);
        background-size: 100% 100%, 200% 200%;
        opacity: 0;
        transition: opacity 0.5s ease;
        z-index: 0; 
        pointer-events: none;
    }

    /* Hover Effect - Lift, Glow, and Shimmer Reveal */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-8px) scale(1.02) !important;
        
        /* Stronger Indigo Glow */
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 0 2px rgba(99, 102, 241, 0.6), 
            0 0 50px rgba(99, 102, 241, 0.4) !important;
            
        border-color: rgba(99, 102, 241, 0.8) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover::after {
        opacity: 1;
    }

    /* Top Accent Bar - Animated Gradient */
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #f43f5e, #3b82f6);
        background-size: 300% 100%;
        animation: gradientMove 8s linear infinite;
        border-radius: 24px 24px 0 0;
        opacity: 0.8;
        z-index: 2;
        pointer-events: none;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 0%; }
    }

    /* Hero Title */
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(120deg, #60a5fa, #a78bfa, #f472b6, #fb923c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -3px;
        line-height: 1.1;
        text-align: center;
        margin: 2rem 0 1rem;
    }

    .hero-subtitle {
        font-size: 1.4rem;
        color: #94a3b8;
        text-align: center;
        font-weight: 500;
        letter-spacing: -0.5px;
    }

    /* Section Headers */
    .section-header {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #e0e7ff, #c7d2fe, #ddd6fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 4rem 0 2rem !important;
        text-align: center;
        letter-spacing: -1.5px;
    }

    /* Card Header */
    .card-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 24px;
    }
    .card-icon {
        font-size: 2rem;
        padding: 12px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.1));
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .card-subtitle {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
    }

    /* Animated Fade In */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeInUp 0.8s ease-out forwards;
    }
    .delay-1 { animation-delay: 0.2s; opacity: 0; }
    .delay-2 { animation-delay: 0.4s; opacity: 0; }
    .delay-3 { animation-delay: 0.6s; opacity: 0; }
    .delay-4 { animation-delay: 0.8s; opacity: 0; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* Button Glow & BRIGHT BLUE FORCE (Includes Download Buttons) */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(90deg, #2563EB, #1D4ED8) !important;
        color: white !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        background: linear-gradient(90deg, #1D4ED8, #1E40AF) !important;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.6) !important;
        border-color: #60A5FA !important;
    }
    /* Specific focus state to prevent default theme override */
    .stButton > button:focus, .stDownloadButton > button:focus {
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.5) !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ====================== NAVBAR & STEPPER ======================
    components.render_navbar()
    st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)
    components.render_stepper(current_step=3)

    # ====================== HERO SECTION ======================
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(90deg, #2563EB 0%, #1d4ed8 100%);
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        color: white;
        margin: 20px 0 40px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .hero-banner-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.02em;
    }
    .hero-banner-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
        max-width: 600px;
        line-height: 1.5;
    }
    .hero-icon-box {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    </style>
    
    <div class="hero-banner">
        <div class="hero-banner-title">
            <!-- Icon imitating the style in the image (Lightning/Analysis) -->
            <div class="hero-icon-box">⚡</div>
            <span>Intelligent Gap Analysis</span>
        </div>
        <div class="hero-banner-subtitle">
            Visualize the bridge between your current skills and your dream job requirements with AI-powered insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====================== DATA PIPELINE ======================
    has_resume_data = "resume_manual" in st.session_state and st.session_state["resume_manual"]
    has_jd_data = "jd_manual" in st.session_state and st.session_state["jd_manual"]
    default_resume = []
    default_jd = []

    if "m2_extracted_skills" in st.session_state:
        m2 = st.session_state["m2_extracted_skills"]
        default_resume = m2.get("resume", [])
        default_jd = m2.get("jd", [])
    elif extract_skills_m1 and (has_resume_data or has_jd_data):
        if has_resume_data:
            default_resume = extract_skills_m1(st.session_state["resume_manual"]) or []
        if has_jd_data:
            default_jd = extract_skills_m1(st.session_state["jd_manual"]) or []

    no_data = not (default_resume or default_jd)
    r_skills = default_resume
    j_skills = default_jd

    if no_data:
        st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
        with st.container(border=True):
            st.warning("No resume or job description found. Please complete Milestone 1 & 2 first.")
            st.info("Your skills will auto-appear here once extracted.")
        st.stop()

    # ====================== CONFIG ======================
    match_thr = 0.75
    partial_thr = 0.45

    with st.expander("Advanced Configuration (Optional)", expanded=False):
        critical_skills = st.multiselect("Critical Skills (Double Weight)", options=j_skills, default=[])

    # ====================== ANALYSIS ENGINE ======================
    precomputed = st.session_state.get("m3_results")
    if precomputed and precomputed.get("resume_skills") == r_skills and precomputed.get("jd_skills") == j_skills:
        # Reconstruct DataFrame from serializable list
        df_plot = pd.DataFrame(precomputed.get("plot_data", []))
        details = precomputed.get("jd_details", [])
        stats = precomputed.get("stats", {}).copy()
    else:
        with st.spinner("AI is mapping 10,000+ semantic connections..."):
            df_plot, details, stats = compute_similarity(r_skills, j_skills, match_thr, partial_thr)

        # Weighted scoring with critical skills
        weighted_score = sum(d['score'] * (2 if d['jd_skill'] in critical_skills else 1) for d in details)
        total_weight = sum(2 if d['jd_skill'] in critical_skills else 1 for d in details)
        final_score = int((weighted_score / total_weight) * 100) if total_weight else stats['overall']
        stats['overall'] = final_score

        st.session_state["m3_results"] = {
            "plot_data": df_plot.to_dict('records'), # Save as list of dicts for JSON serialization
            "jd_details": details, 
            "stats": stats,
            "resume_skills": r_skills, 
            "jd_skills": j_skills, 
            "critical_skills": critical_skills
        }
        
        # Persist results immediately
        components.save_progress()

    # ====================== 1. EXECUTIVE SUMMARY ======================
    st.markdown('<h2 class="section-header animate-fade-in delay-1">Executive Summary</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon">Target</div><div><div class="card-title">Match Scorecard</div><div class="card-subtitle">AI-Powered Precision Analysis</div></div></div>', unsafe_allow_html=True)
            c1, c2 = st.columns([1.3, 1])
            with c1:
                st.plotly_chart(charts.get_gauge_chart(stats['overall']), use_container_width=True, config={'displayModeBar': False})
            with c2:
                st.markdown(textwrap.dedent(f"""\
                    <div style="display:grid; gap:12px; margin-top:20px;">
                        <div style="background:#10b98120; padding:14px; border-radius:12px; border:1px solid #10b98140;">
                            <div style="display:flex; justify-content:space-between;"><span>Matched</span><span style="font-weight:800; color:#10b981;">{stats['matched']}</span></div>
                        </div>
                        <div style="background:#f59e0b20; padding:14px; border-radius:12px; border:1px solid #f59e0b40;">
                            <div style="display:flex; justify-content:space-between;"><span>Partial</span><span style="font-weight:800; color:#f59e0b;">{stats['partial']}</span></div>
                        </div>
                        <div style="background:#ef444420; padding:14px; border-radius:12px; border:1px solid #ef444440;">
                            <div style="display:flex; justify-content:space-between;"><span>Missing</span><span style="font-weight:800; color:#ef4444;">{stats['missing']}</span></div>
                        </div>
                    </div>
                """), unsafe_allow_html=True)

    with col2:
        score = stats['overall']
        if score >= 90:
            title, badge, color = "Unicorn Candidate", "Elite Tier", "#8b5cf6"
        elif score >= 75:
            title, badge, color = "Top Contender", "Interview Ready", "#10b981"
        elif score >= 55:
            title, badge, color = "Rising Star", "Strong Foundation", "#f59e0b"
        else:
            title, badge, color = "Aspiring Builder", "Growth Phase", "#ef4444"

        with st.container(border=True):
            st.markdown(textwrap.dedent(f"""\
                <div style="text-align:center; padding:20px 0;">
                    <div style="background:{color}20; color:{color}; padding:6px 16px; border-radius:16px; font-weight:700; font-size:0.8rem; display:inline-block; border:1px solid {color}40;">
                        {badge}
                    </div>
                    <div style="font-size:2rem; font-weight:900; margin:16px 0; color:#f8fafc;">{title}</div>
                    <div style="background:#1e293b; padding:16px; border-radius:16px; border:1px solid rgba(255,255,255,0.08);">
                        <div style="font-size:0.9rem; color:#94a3b8;">Market Position</div>
                        <div style="font-size:1.5rem; font-weight:800; color:{color};">Top {100-score}% Globally</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)

    st.markdown('<h2 class="section-header animate-fade-in delay-2">Skill Landscape</h2>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.6, 1])
    with c1:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon">Chart</div><div><div class="card-title">Similarity Matrix</div><div class="card-subtitle">Neural Embedding Correlations</div></div></div>', unsafe_allow_html=True)
            if st.button("Refresh Analysis", key="refresh"):
                if "m3_results" in st.session_state: del st.session_state["m3_results"]
                st.rerun()
            st.plotly_chart(charts.get_bubble_chart(df_plot), use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon">Radar</div><div><div class="card-title">Category Coverage</div><div class="card-subtitle">Skill Distribution Radar</div></div></div>', unsafe_allow_html=True)
            cats = SKILL_CATEGORIES.keys()
            r_counts = Counter(get_skill_category(s) for s in r_skills)
            j_counts = Counter(get_skill_category(s) for s in j_skills)
            fig = charts.get_radar_chart(
                dict((c, r_counts.get(c, 0)) for c in cats),
                dict((c, j_counts.get(c, 0)) for c in cats)
            )
            st.plotly_chart(fig, use_container_width=True)


    # ====================== 3. GAP ANALYSIS ======================
    st.markdown('<h2 class="section-header animate-fade-in delay-3">Gap Analysis</h2>', unsafe_allow_html=True)
    c_gap1, c_gap2 = st.columns([1, 1.5])

    # Critical Gaps
    with c_gap1:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(239,68,68,0.1); border-color:rgba(239,68,68,0.2);">⚠️</div><div><div class="card-title">Critical Gaps</div><div class="card-subtitle">Immediate Attention Required</div></div></div>', unsafe_allow_html=True)
            
            crit_missing = [d for d in details if d['jd_skill'] in critical_skills and d['category'] == "Low Match"]
            other_missing = [d for d in details if d['jd_skill'] not in critical_skills and d['category'] == "Low Match"]
            display_missing = (crit_missing + other_missing)[:5]

            if display_missing:
                for item in display_missing:
                    val = int(item['score']*100)
                    is_crit = item['jd_skill'] in critical_skills
                    badge_html = '<span style="background:#ef444420; color:#fca5a5; padding:2px 8px; border-radius:6px; font-size:0.6rem; border:1px solid #ef444440; margin-left:8px;">CRITICAL</span>' if is_crit else ""
                    
                    st.markdown(textwrap.dedent(f"""\
                        <div style="background:rgba(255,255,255,0.03); border-radius:12px; padding:12px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.05);">
                            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                                <div style="font-weight:600; color:#f1f5f9;">{item['jd_skill']}{badge_html}</div>
                                <div style="font-size:0.8rem; color:#94a3b8;">{val}% Match</div>
                            </div>
                            <div style="height:4px; background:rgba(255,255,255,0.1); border-radius:2px;">
                                <div style="width:{val}%; height:100%; background:#ef4444; border-radius:2px; box-shadow:0 0 10px rgba(239,68,68,0.4);"></div>
                            </div>
                        </div>
                    """), unsafe_allow_html=True)
            else:
                 st.markdown('<div style="text-align:center; padding:20px; color:#10b981;">🎉 All critical skills covered!</div>', unsafe_allow_html=True)

    # Heatmap
    with c_gap2:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(245,158,11,0.1); border-color:rgba(245,158,11,0.2);">🔥</div><div><div class="card-title">Skill Heatmap</div><div class="card-subtitle">Correlation Analysis</div></div></div>', unsafe_allow_html=True)
            if not df_plot.empty:
                st.plotly_chart(charts.get_heatmap(df_plot), use_container_width=True)

    # Detailed Table
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(59,130,246,0.1); border-color:rgba(59,130,246,0.2);">📋</div><div><div class="card-title">Deep Dive</div><div class="card-subtitle">Full Metrics Breakdown</div></div></div>', unsafe_allow_html=True)
        
        table_data = [{
            "Skill": d['jd_skill'], 
            "Best Match": d['resume_match'],
            "Score": d['score'],
            "Status": d['category'],
            "Critical": "Yes" if d['jd_skill'] in critical_skills else "No"
        } for d in details]
        
        st.dataframe(
            pd.DataFrame(table_data),
            column_config={
                "Score": st.column_config.ProgressColumn("Similarity", min_value=0, max_value=1, format="%.2f"),
                "Critical": st.column_config.TextColumn("Critical", width="small")
            },
            use_container_width=True,
            hide_index=True
        )

    # ====================== 4. RECOMMENDED ACTIONS ======================
    st.markdown('<h2 class="section-header animate-fade-in delay-4">Action Plan</h2>', unsafe_allow_html=True)
    
    missing_high_pri = [d for d in details if d['category'] == "Low Match"]
    missing_high_pri.sort(key=lambda x: (x['jd_skill'] not in critical_skills, x['score']))
    
    if missing_high_pri:
        cols = st.columns(3)
        for i, m in enumerate(missing_high_pri[:3]):
            skill = m['jd_skill']
            hours = len(skill) * 2 + 10
            
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(textwrap.dedent(f"""
                        <div style="margin-bottom:15px;">
                            <span style="background:#3b82f620; color:#60a5fa; padding:4px 10px; border-radius:8px; font-size:0.7rem; font-weight:700;">RECOMMENDED</span>
                            <span style="float:right; color:#94a3b8; font-size:0.8rem;">⏱️ {hours}h</span>
                        </div>
                        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc; margin-bottom:10px;">{skill}</div>
                        <div style="color:#94a3b8; font-size:0.9rem; margin-bottom:20px; min-height:40px;">Mastering this skill is the fastest way to improve your score.</div>
                        <a href="https://www.coursera.org/search?query={skill}" target="_blank" style="display:block; text-align:center; background:linear-gradient(90deg, #2563EB, #1D4ED8); color:white; padding:12px; border-radius:12px; text-decoration:none; font-weight:600; box-shadow:0 4px 10px rgba(37, 99, 235, 0.4); margin-top:10px; margin-bottom:10px;">Start Learning →</a>
                    """), unsafe_allow_html=True)

    # ====================== 5. SIMULATOR ======================
    sim_missing = [d for d in details if d['category'] in ["Low Match", "Partial Match"]]
    if sim_missing:
        st.markdown('<br>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(139,92,246,0.1); border-color:rgba(139,92,246,0.2);">🔮</div><div><div class="card-title">Career Simulation Lab</div><div class="card-subtitle">Project Your Future Growth</div></div></div>', unsafe_allow_html=True)
            
            selected_sim = []
            c_sim_cols = st.columns(3)
            for i, item in enumerate(sim_missing):
                with c_sim_cols[i%3]:
                    if st.checkbox(f"{item['jd_skill']} (+{100-int(item['score']*100)}%)", key=f"sim_{i}"):
                        selected_sim.append(item)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Simulate New Score", type="primary", use_container_width=True):
                if selected_sim:
                    # Calc new score
                    current_weighted = sum((d['score']) * (2 if d['jd_skill'] in critical_skills else 1) for d in details)
                    sim_add = 0
                    for s in selected_sim:
                        weight = 2 if s['jd_skill'] in critical_skills else 1
                        # Upgrade from current score to 1.0
                        gain = (1.0 - s['score']) * weight
                        sim_add += gain
                    
                    new_weighted = current_weighted + sim_add
                    
                    # Recalculate total_weight for local scope context
                    total_weight = sum(2 if d['jd_skill'] in critical_skills else 1 for d in details)
                    
                    new_final = int((new_weighted / total_weight) * 100)
                    
                    st.markdown(textwrap.dedent(f"""
                        <div style="margin-top:20px; padding:40px; background:linear-gradient(135deg, #059669, #047857); border-radius:20px; text-align:center; color:white; box-shadow:0 20px 50px -10px rgba(5,150,105,0.5); border:1px solid rgba(255,255,255,0.2);">
                            <div style="font-size:1rem; opacity:0.9; text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;">Projected Capability</div>
                            <div style="font-size:5rem; font-weight:900; line-height:1; margin-bottom:10px;">{new_final}%</div>
                            <div style="font-size:1.2rem; background:rgba(0,0,0,0.2); display:inline-block; padding:8px 20px; border-radius:12px;">+{new_final - stats['overall']}% Growth Potential</div>
                        </div>
                    """), unsafe_allow_html=True)
                    st.balloons()

    # ====================== 6. AI COACH ======================
    st.markdown('<h2 class="section-header animate-fade-in delay-2">AI Career Coach</h2>', unsafe_allow_html=True)
    c_coach1, c_coach2 = st.columns(2)

    with c_coach1:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon">🎤</div><div><div class="card-title">Interview Agent</div><div class="card-subtitle">Strategic Interpretation</div></div></div>', unsafe_allow_html=True)
            if missing_high_pri:
                top_gap = missing_high_pri[0]['jd_skill']
                st.markdown(textwrap.dedent(f"""
                    <div style="background:rgba(59,130,246,0.1); border-left:4px solid #3b82f6; padding:16px; border-radius:0 12px 12px 0; margin-bottom:20px;">
                        <div style="font-size:0.8rem; color:#93c5fd; font-weight:700; letter-spacing:1px; margin-bottom:4px;">KEY TOPIC</div>
                        <div style="font-size:1.2rem; font-weight:700; color:white;">{top_gap}</div>
                    </div>
                    <div style="color:#cbd5e1; font-weight:500; margin-bottom:10px;">Likely Interview Questions:</div>
                    <ul style="color:#94a3b8; font-size:0.95rem; line-height:1.6; padding-left:20px;">
                        <li>"Describe a situation where you had to implement <b>{top_gap}</b> in a production environment."</li>
                        <li>"How would you handle edge cases associated with <b>{top_gap}</b>?"</li>
                    </ul>
                """), unsafe_allow_html=True)
            else:
                st.success("You're a strong match! Focus on leadership and soft skills.")

    with c_coach2:
        with st.container(border=True):
            st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(16,185,129,0.1); border-color:rgba(16,185,129,0.2);">📝</div><div><div class="card-title">Resume Optimizer</div><div class="card-subtitle">ATS Keyword Injection</div></div></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="display:grid; gap:12px;">
                <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px;">
                    <span style="color:#3b82f6; font-weight:700;">Architected</span> <span style="color:#64748b;">for System Design</span>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px;">
                    <span style="color:#10b981; font-weight:700;">Orchestrated</span> <span style="color:#64748b;">for Leadership</span>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px;">
                    <span style="color:#f59e0b; font-weight:700;">Deployed</span> <span style="color:#64748b;">for CI/CD</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ====================== EXPORT ======================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="card-header"><div class="card-icon" style="background:rgba(14,165,233,0.1); border-color:rgba(14,165,233,0.2);">📤</div><div><div class="card-title">Data Vault</div><div class="card-subtitle">Export Intelligence Report</div></div></div>', unsafe_allow_html=True)
        
        csv = pd.DataFrame(details).to_csv(index=False).encode('utf-8')
        c1, c2 = st.columns([3,1])
        with c1:
             st.markdown("Download the full semantic analysis dataset including vector scores and partial match confidence levels.")
        with c2:
            st.download_button("Download CSV", data=csv, file_name="ai_skill_gap_analysis.csv", mime="text/csv", type="primary", use_container_width=True)


    # Final Navigation
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    
    def proceed_to_m4():
        # Pre-compute heavy M4 report data
        if "m3_results" in st.session_state:
            results = st.session_state["m3_results"]
            jd_details = results["jd_details"]
            critical_skills = results.get("critical_skills", [])
            
            # 1. Identify Gaps
            all_gaps = [d['jd_skill'] for d in jd_details if d['category'] in ["Low Match", "Partial Match"]]
            
            # 2. Roadmap Generation
            import math
            total_skills = len(all_gaps)
            chunk_size = math.ceil(total_skills / 3) if total_skills > 0 else 1
            w1 = all_gaps[:chunk_size]
            w2 = all_gaps[chunk_size:chunk_size*2]
            w3 = all_gaps[chunk_size*2:]
            
            roadmap = [
                {"title": "Week 1: Foundations", "focus": w1 if w1 else ["Core Fundaments"], "desc": "Syntax & Basic Principles", "tasks": ["Crash Course", "Docs Reading"]},
                {"title": "Week 2: Application", "focus": w2 if w2 else ["Advanced Concepts"], "desc": "Build scripts & debug", "tasks": ["Code-Along", "Small Scripts"]},
                {"title": "Week 3: Integration", "focus": w3 if w3 else ["System Integration"], "desc": "Connect APIs & DBs", "tasks": ["Mini Project", "API integration"]},
                {"title": "Week 4: Mastery", "focus": ["Interview Prep", "System Design"], "desc": "Mock Interviews & Resume", "tasks": ["Mock Interview", "Portfolio Polish"]}
            ]
            
            # 3. Capstone Projects
            cats = set([get_skill_category(s) for s in all_gaps])
            projects = []
            if "Data Science" in cats:
                projects.append({"title": "Predictive Analytics Dashboard", "desc": "Analyze trends & predict outcomes.", "tags": ["Data Viz", "ML"], "color": "#F472B6"})
            elif "Frameworks" in cats:
                projects.append({"title": "Full-Stack Task Manager", "desc": "Scalable CRUD app with Auth.", "tags": ["FullStack", "API"], "color": "#34D399"})
            else:
                projects.append({"title": "Skill Showcase Portfolio", "desc": "Personal website with resume.", "tags": ["Web", "Design"], "color": "#60A5FA"})
            
            # 4. Interview Questions
            questions = []
            gaps_lower = [g.lower() for g in all_gaps]
            if "python" in gaps_lower: questions.append(("🐍 Python", "Difference between list and tuple?"))
            if "react" in gaps_lower: questions.append(("⚛️ React", "Explain Virtual DOM?"))
            if "aws" in gaps_lower: questions.append(("☁️ Cloud", "S3 vs EBS use cases?"))
            if not questions: questions.append(("🚀 System Design", "Design a URL shortener."))

            st.session_state["m4_data"] = {
                "roadmap": roadmap,
                "projects": projects,
                "questions": questions,
                "all_gaps": all_gaps,
                "generated_at": time.time()
            }
            
            # Persist data
            components.save_progress()
            
        navigate_to("Milestone 4: Dashboard & Report")

    with col2:
        c1, c2 = st.columns(2)
        with c1:
            st.button("← Milestone 2", type="primary", use_container_width=True, on_click=navigate_to, args=("Milestone 2: Skill Extraction",))
        with c2:
            st.button("Milestone 4 →", type="primary", use_container_width=True, on_click=proceed_to_m4)

    components.render_footer()

if __name__ == "__main__":
    st.set_page_config(page_title="AI Career Gap Analysis • Milestone 3", layout="wide", initial_sidebar_state="collapsed")
    app()