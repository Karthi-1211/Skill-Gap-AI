import streamlit as st
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Milestone 3 • Skill Gap Analysis and Similarity Matching",
    page_icon="📊",
    layout="wide",
)

# -------------------------------------------------------
# THEME COLORS (to mimic your screenshot)
# -------------------------------------------------------
PURPLE = "#6C3CF0"
LIGHT_PURPLE = "#763CF5"
GREEN = "#34C759"
ORANGE = "#FFB020"
RED = "#FF3B30"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F5F7FB"
TEXT_MAIN = "#111827"
TEXT_MUTED = "#6B7280"
BORDER = "#E5E7EB"

# -------------------------------------------------------
# GLOBAL CSS – header, cards, etc.
# -------------------------------------------------------
st.markdown(
    f"""
<style>
html, body, .stApp {{
    background: {PAGE_BG};
    font-family: system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}}

.block-container {{
    padding-top: 0.5rem;
    padding-bottom: 2.5rem;
}}

.hero {{
  background: {PURPLE};
  color: white;
  padding: 1.3rem 1.6rem;
  border-radius: 0.9rem;
  box-shadow: 0 14px 30px rgba(15,23,42,0.45);
  margin-bottom: 1.5rem;
}}

.hero-title {{
    font-size: 1.5rem;
    font-weight: 700;
}}

.hero-sub {{
    font-size: 0.9rem;
    margin-top: 0.35rem;
    opacity: 0.9;
}}

.hero-meta {{
    font-size: 0.9rem;
    margin-top: 0.15rem;
}}

.hero-meta span {{
    font-weight: 600;
}}

.section-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {PURPLE};
    margin-bottom: 0.5rem;
}}

.main-card {{
    background: {CARD_BG};
    border-radius: 0.9rem;
    border: 1px solid {BORDER};
    padding: 1.0rem 1.0rem 0.8rem 1.0rem;
    box-shadow: 0 10px 30px rgba(15,23,42,0.05);
}}

.sub-card-title {{
    font-size: 0.9rem;
    font-weight: 600;
    color: {TEXT_MAIN};
    margin-bottom: 0.6rem;
}}

.legend-bar {{
    display:flex;
    align-items:center;
    font-size:0.8rem;
    margin-top:0.4rem;
}}

.legend-item {{
    display:flex;
    align-items:center;
    margin-right:1rem;
}}

.legend-dot {{
    width:12px;
    height:12px;
    border-radius:999px;
    margin-right:0.25rem;
}}

.stat-card {{
    background: #F9FAFB;
    border-radius: 0.7rem;
    border: 1px solid {BORDER};
    padding: 0.8rem 0.9rem;
    margin-bottom: 0.6rem;
}}

.stat-label {{
    font-size: 0.8rem;
    color: {TEXT_MUTED};
}}

.stat-value {{
    font-size: 1.3rem;
    font-weight: 700;
    color: {TEXT_MAIN};
    margin-top: 0.15rem;
}}

.missing-card {{
    background: {CARD_BG};
    border-radius: 0.9rem;
    border: 1px solid {BORDER};
    padding: 0.8rem 0.9rem;
    box-shadow: 0 10px 25px rgba(15,23,42,0.04);
}}

.missing-item {{
    display:flex;
    justify-content:space-between;
    align-items:center;
    border-radius:0.8rem;
    border:1px solid {BORDER};
    padding:0.65rem 0.7rem;
    margin-top:0.4rem;
}}

.badge-high {{
  padding:0.15rem 0.7rem;
  border-radius:999px;
  font-size:0.72rem;
  background:rgba(255,59,48,0.08);
  color:{RED};
  border:1px solid rgba(255,59,48,0.5);
}}

.skill-type {{
    font-size:0.75rem;
    color:{TEXT_MUTED};
}}

.icon-circle {{
    width:30px;
    height:30px;
    border-radius:999px;
    background:rgba(108,76,240,0.08);
    display:flex;
    align-items:center;
    justify-content:center;
    color:{PURPLE};
    margin-right:0.6rem;
}}

.missing-head {{
    display:flex;
    align-items:center;
}}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# LOAD SENTENCE-BERT (cached)
# -------------------------------------------------------
@st.cache_resource(show_spinner=True)
def load_model():
    # General sentence embedding model suitable for semantic similarity
    # See official docs: https://www.sbert.net
    return SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------------------------------------
# SKILL SIMILARITY LOGIC
# -------------------------------------------------------
def analyze_skills(resume_skills, jd_skills,
                   match_thr=0.8,
                   partial_thr=0.5):
    """
    Compute cosine similarity between JD skills and resume skills
    using Sentence-BERT embeddings, and bucket into:
    Matched / Partial / Missing.
    """
    resume_skills = [s.strip() for s in resume_skills if s.strip()]
    jd_skills = [s.strip() for s in jd_skills if s.strip()]

    if not resume_skills or not jd_skills:
        return None, None, None

    model = load_model()
    all_txt = resume_skills + jd_skills
    emb = model.encode(all_txt, normalize_embeddings=True)
    res_emb = emb[: len(resume_skills)]
    jd_emb = emb[len(resume_skills):]

    sim = cosine_similarity(jd_emb, res_emb)
    jd_idx = []
    buckets = []
    points = []

    matched = partial = missing = 0

    for i, jd_skill in enumerate(jd_skills):
        row = sim[i]
        best_j = int(np.argmax(row))
        best_skill = resume_skills[best_j]
        score = float(row[best_j])

        if score >= match_thr:
            cat = "High Match"
            matched += 1
        elif score >= partial_thr:
            cat = "Partial Match"
            partial += 1
        else:
            cat = "Low Match"
            missing += 1

        jd_idx.append(
            dict(
                jd_skill=jd_skill,
                resume_match=best_skill,
                score=score,
                category=cat,
            )
        )

        # For bubble chart: x = resume skill, y = JD skill
        points.append(
            dict(
                jd_skill=jd_skill,
                resume_skill=best_skill,
                score=score,
                category=cat,
            )
        )

    overall = round((matched + 0.5 * partial) / len(jd_skills) * 100, 0)

    stats = dict(
        overall=overall,
        matched=matched,
        partial=partial,
        missing=missing,
        total=len(jd_skills),
    )

    matrix = pd.DataFrame(points)
    return matrix, jd_idx, stats


# -------------------------------------------------------
# HERO HEADER (purple bar)
# -------------------------------------------------------
st.markdown(
    f"""
<div class="hero">
  <div class="hero-title">Milestone 3: Skill Gap Analysis and Similarity Matching Module (Weeks 5–6)</div>
  <div class="hero-sub">
    Module: <span>Skill Gap Analysis and Similarity Matching</span> •
    <span>BERT embeddings for skills</span> •
    <span>Cosine similarity comparison</span> •
    <span>Missing skills identification and ranking</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# INPUTS
# -------------------------------------------------------
st.markdown('<div class="section-title">Skill Gap Analysis Interface</div>', unsafe_allow_html=True)

with st.container():
    top_col1, top_col2 = st.columns([1.2, 1])

    with top_col1:
        with st.expander("Configure Skill Sets", expanded=True):
            default_resume = [
                "ML", "SQL", "Communication", "Advanced Statistics",
                "Teamwork", "Problem Solving"
            ]
            default_jd = [
                "ML", "SQL", "Communication", "Advanced Statistics",
                "NoSQL", "Team Leadership"
            ]

            resume_text = st.text_area(
                "Resume Skills (comma separated)",
                value=", ".join(default_resume),
                height=70,
            )
            jd_text = st.text_area(
                "JD Skills (comma separated)",
                value=", ".join(default_jd),
                height=70,
            )
            match_thr = st.slider(
                "High Match threshold",
                0.6, 0.95, 0.8, 0.01,
            )
            partial_thr = st.slider(
                "Partial Match threshold",
                0.3, match_thr - 0.05, 0.5, 0.01,
            )
            run_btn = st.button("Run Skill Gap Analysis", use_container_width=True)

    with top_col2:
        st.info(
            """
            **How it works**

            • Skills from the resume and JD are encoded with a Sentence-BERT model  
            • We compute cosine similarity between each JD skill and all resume skills  
            • Each JD skill is tagged as **High Match**, **Partial Match** or **Low Match (gap)**  
            • Results are shown as a similarity **bubble matrix**, summary cards, and a donut chart
            """,
            icon="ℹ️",
        )

# -------------------------------------------------------
# RUN
# -------------------------------------------------------
if run_btn:
    resume_skills = [x.strip() for x in resume_text.split(",") if x.strip()]
    jd_skills = [x.strip() for x in jd_text.split(",") if x.strip()]

    with st.spinner("Computing BERT embeddings and cosine similarity..."):
        matrix_df, jd_details, stats = analyze_skills(
            resume_skills, jd_skills,
            match_thr=match_thr, partial_thr=partial_thr
        )

    if matrix_df is None:
        st.warning("Please provide at least one Resume skill and one JD skill.")
    else:
        # ---------------------------------------------------
        # MAIN WHITE CARD (same layout as screenshot)
        # ---------------------------------------------------
        main_left, main_right = st.columns([1.3, 1])

        # ---------------- Left: Similarity Matrix + legend + Missing Skills box
        with main_left:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown('<div class="sub-card-title">Similarity Matrix</div>', unsafe_allow_html=True)

            # Bubble scatter: x resume_skill, y jd_skill
            color_map = {
                "High Match": GREEN,
                "Partial Match": ORANGE,
                "Low Match": RED,
            }
            matrix_df["size"] = matrix_df["score"] * 30 + 10

            fig_scatter = px.scatter(
                matrix_df,
                x="resume_skill",
                y="jd_skill",
                size="size",
                size_max=40,
                color="category",
                hover_data=["score"],
                color_discrete_map=color_map,
            )
            fig_scatter.update_traces(marker=dict(line=dict(width=0)))
            fig_scatter.update_layout(
                xaxis_title="",
                yaxis_title="",
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,1)",
                legend=dict(orientation="h", y=-0.18),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            st.markdown(
                f"""
<div class="legend-bar">
  <div class="legend-item">
    <div class="legend-dot" style="background:{GREEN};"></div> High Match (80–100%)
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:{ORANGE};"></div> Partial Match (50–79%)
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:{RED};"></div> Low Match (0–49%)
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("---", unsafe_allow_html=True)

            # Missing skills card at bottom left (like AWS Cloud Services)
            st.markdown('<div class="sub-card-title">Missing Skills</div>', unsafe_allow_html=True)

            with st.container():
                st.markdown('<div class="missing-card">', unsafe_allow_html=True)

                # pick top 1–2 gaps based on score ascending
                low_items = [x for x in jd_details if x["category"] == "Low Match"]
                low_items = sorted(low_items, key=lambda x: x["score"])[:2]

                if not low_items:
                    st.success("No severe gaps detected – all JD skills have at least partial matches ✅")
                else:
                    # show first like AWS Cloud Services style
                    first = low_items[0]
                    st.markdown(
                        f"""
<div class="missing-item">
  <div class="missing-head">
    <div class="icon-circle">☁️</div>
    <div>
      <div><strong>{first['jd_skill']}</strong></div>
      <div class="skill-type">Technical Skill</div>
    </div>
  </div>
  <div class="badge-high">High</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                    # if more, show simple text list
                    if len(low_items) > 1:
                        for extra in low_items[1:]:
                            st.markdown(
                                f"""
<div style="margin-top:0.4rem; font-size:0.8rem; color:{TEXT_MUTED};">
 • {extra['jd_skill']} (closest: {extra['resume_match']}, similarity {extra['score']:.2f})
</div>
""",
                                unsafe_allow_html=True,
                            )

                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- Right: Skill Match Overview box
        with main_right:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown('<div class="sub-card-title">Skill Match Overview</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f"""
<div class="stat-card">
  <div class="stat-label">Overall Match</div>
  <div class="stat-value">{int(stats['overall'])}%</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"""
<div class="stat-card">
  <div class="stat-label">Matched Skills</div>
  <div class="stat-value">{stats['matched']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            c3, c4 = st.columns(2)
            with c3:
                st.markdown(
                    f"""
<div class="stat-card">
  <div class="stat-label">Partial Matches</div>
  <div class="stat-value">{stats['partial']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            with c4:
                st.markdown(
                    f"""
<div class="stat-card">
  <div class="stat-label">Missing Skills</div>
  <div class="stat-value">{stats['missing']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            # Donut chart
            donut_df = pd.DataFrame(
                {
                    "Status": ["Matched Skills", "Partial Matches", "Missing Skills"],
                    "Count": [stats["matched"], stats["partial"], stats["missing"]],
                }
            )
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=donut_df["Status"],
                        values=donut_df["Count"],
                        hole=0.6,
                        marker=dict(
                            colors=[GREEN, ORANGE, RED],
                        ),
                    )
                ]
            )
            fig_donut.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)
