import streamlit as st
import re
import textwrap

from datetime import datetime
from collections import Counter

import base64
import json
import streamlit.components.v1 as st_components

SKILL_CATEGORIES = {
    "Languages": ["python", "java", "c++", "javascript", "html", "css", "sql", "bash", "r", "go", "ruby", "php", "swift", "kotlin"],
    "Frameworks": ["react", "node.js", "django", "flask", "tensorflow", "pytorch", "scikit-learn", "angular", "vue", "spring", "fastapi", "pandas", "numpy"],
    "Cloud/DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "git", "jenkins", "linux", "jira", "terraform", "ansible", "ci/cd"],
    "Data Science": ["machine learning", "deep learning", "nlp", "computer vision", "statistics", "analysis", "visualization", "power bi", "tableau", "excel", "spark", "hadoop"],
    "Soft Skills": ["communication", "leadership", "teamwork", "problem solving", "time management", "adaptability", "critical thinking", "creativity", "collaboration", "decision making", "emotional intelligence", "negotiation", "conflict resolution"]
}

TECHNICAL_SKILLS = [
    "python", "java", "c++", "sql", "html", "css", "javascript", "react", "node.js",
    "tensorflow", "pytorch", "machine learning", "data analysis", "data visualization",
    "aws", "azure", "gcp", "power bi", "tableau", "django", "flask", "scikit-learn", "nlp",
    "docker", "kubernetes", "git", "jenkins", "linux", "excel", "spark", "hadoop"
]

SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "time management",
    "adaptability", "critical thinking", "creativity", "collaboration", "decision making",
    "emotional intelligence", "negotiation", "conflict resolution"
]

technical_skills = TECHNICAL_SKILLS
soft_skills = SOFT_SKILLS
skill_categories = SKILL_CATEGORIES

# -------------------------------------------------------
# NLP MODELS & EXTRACTION
# -------------------------------------------------------
@st.cache_resource
def load_nlp():
    import spacy
    try:
        
        return spacy.load("en_core_web_sm", disable=["parser", "ner", "textcat"])
    except:
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm", disable=["parser", "ner", "textcat"])

def clean_text(text: str) -> str:
    import re
    # Basic cleaning
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\+\-\.#]", " ", text) 
    return text.lower().strip()

@st.cache_data(ttl=3600)
def extract_skills(text):
    """
    Extracts skills using a hybrid approach:
    1. Direct phrase matching from dictionary (High Precision).
    2. SpaCy Lemmatization to catch variations (e.g. 'Developing' -> 'Develop').
    """
    nlp = load_nlp()
    doc = nlp(text.lower())
    
    # 1. Lemmatized tokens for variation matching
    lemmas = set([token.lemma_ for token in doc if not token.is_stop])
    text_clean = clean_text(text)
    
    found_tech = set()
    found_soft = set()
    
    # Check Technical Skills
    for skill in TECHNICAL_SKILLS:
        # Check explicit phrase in raw text (e.g. "machine learning")
        if skill in text_clean:
            found_tech.add(skill.title())
        # Check single-word lemma match (e.g. "python" in lemmas)
        elif len(skill.split()) == 1 and skill in lemmas:
             found_tech.add(skill.title())
             
    # Check Soft Skills
    for skill in SOFT_SKILLS:
        if skill in text_clean:
             found_soft.add(skill.title())
        elif len(skill.split()) == 1 and skill in lemmas:
             found_soft.add(skill.title())
             
    return list(found_tech), list(found_soft)

def count_skill_frequency(text, skills):
    import re
    text_clean = clean_text(text)
    counts = {}
    for skill in skills:
        # Improved Regex for word boundary
        pattern = re.compile(r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)')
        counts[skill] = len(pattern.findall(text_clean))
    return counts

def highlight_text(text, skills):
    import re
    if not text:
        return ""
    
    # Sort by length to match longest phrases first
    skills = sorted(skills, key=len, reverse=True)
    if not skills:
        return text
        
    pattern_str = '|'.join(re.escape(s) for s in skills)
    pattern = re.compile(r'(?i)(?<!\w)(' + pattern_str + r')(?!\w)')
    
    def replace_func(match):
        return f'<span class="highlight-skill">{match.group(0)}</span>'
        
    return pattern.sub(replace_func, text)

def skill_confidences(skills):
    n = len(skills)
    if n == 0:
        return {}
    start = 96
    step = 10 / max(n - 1, 1)
    conf = {}
    for i, s in enumerate(skills):
        conf[s] = max(75, round(start - i * step))
    return conf

def get_skill_category(skill):
    s_lower = skill.lower()
    for cat, skills in SKILL_CATEGORIES.items():
        if any(k in s_lower for k in skills):
            return cat
    return "General"

def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def app():
    import components as ui_components
   
    import components
    st.markdown(components.get_page_css(), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        /* M2 Specific Styles */
        /* Dashboard Cards */
        .metric-box {
            background: var(--card-bg);
            border: var(--card-border);
            border-radius: 16px;
            padding: 35px;
            text-align: center;
            box-shadow: var(--card-shadow);
            transition: transform 0.2s;
            margin-bottom: 20px;
        }
        .metric-box:hover { transform: translateY(-5px); }
        .metric-val { font-size: 5rem; font-weight: 800; color: #3B82F6; }
        .metric-lbl { font-size: 2rem; color: #cbd5e1; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 10px; font-weight: 700; }

        /* Highlight Box */
        .highlight-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #334155;
            border-left: 5px solid #10b981; 
            padding: 25px;
            border-radius: 12px;
            font-family: 'Inter', sans-serif;
            font-size: 1.05rem;  
            line-height: 1.9;
            color: #f1f5f9;
            margin-bottom: 25px;
            height: 400px;  
            overflow-y: auto;
            white-space: pre-wrap;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        /* Highlighted Skill Span - GREEN */
        .highlight-skill {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            border-bottom: 2px solid #10b981;
            font-size: 1rem;
        }
        
        /* Detailed List Styling */
        .detail-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255,255,255,0.03);
            margin-bottom: 12px;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: background 0.2s;
        }
        .detail-row:hover { background: rgba(255,255,255,0.06); }
        .detail-info { flex-grow: 1; }
        .detail-title { font-weight: 600; color: var(--text-color); font-size: 1.3rem; }
        .detail-subtitle { font-size: 0.95rem; color: var(--muted-color); margin-top: 4px; }
        .detail-score { font-weight: 700; color: var(--success-color); font-size: 1.3rem; }
        
        /* Skill Tags */
        .skill-tag {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0 5px 5px 0;
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        /* Category Headers */
        .category-header {
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-color);
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 8px;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(59, 130, 246, 0.1);
            border-bottom: 2px solid var(--accent-color);
        }
        
        /* Skill Chips */
        .skill-chip {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 16px;
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0 6px 6px 0;
        }
        .skill-chip-soft {
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        /* Summary Strip - Larger */
        .summary-strip {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.2);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
        }
        
        /* Small Chips for Summary - Larger */
        .chip-small {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 0.9rem;  
            margin: 0 6px 6px 0;
            background: rgba(255, 255, 255, 0.1);
            color: #f1f5f9;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
            font-weight: 500;
        }
        .chip-missing {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border-color: rgba(239, 68, 68, 0.4);
        }
        .chip-extra {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
            border-color: rgba(16, 185, 129, 0.4);
        }

        /* Blue Primary Button Styling */
        .stButton button[kind="primary"] {
            background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1.1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(4px);
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.6);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 1. NAVBAR & SIDEBAR (Shared)
    import components
    components.render_navbar()
   
    ui_components.scroll_to_top(smooth=False, delay_ms=50)

     
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    components.render_stepper(current_step=2)

    logo_svg = '<svg width="35" height="35" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon"><defs><linearGradient id="grad4" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#22D3EE" /><stop offset="100%" stop-color="#3B82F6" /></linearGradient><filter id="glow4" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><rect x="10" y="10" width="44" height="44" rx="12" stroke="url(#grad4)" stroke-width="4" fill="none"/><path d="M24 36L30 36L28 46L40 28L34 28L36 18L24 36Z" fill="white" filter="url(#glow4)"/><circle cx="32" cy="8" r="3" fill="#22D3EE"/><circle cx="32" cy="56" r="3" fill="#3B82F6"/><circle cx="8" cy="32" r="3" fill="#22D3EE"/><circle cx="56" cy="32" r="3" fill="#3B82F6"/></svg>'
    
    st.markdown(textwrap.dedent(f"""
        <div class="hero-section">
            <div class="hero-title">
                {logo_svg}
                <div>AI Skill Extraction Engine</div>
            </div>
            <div class="hero-sub">Instantly decode resumes and job descriptions to reveal hidden technical and soft skills.</div>
        </div>
    """), unsafe_allow_html=True)

    # ------------------------------------------
    # SESSION STATE
    # ------------------------------------------
    if "last_updated" not in st.session_state:
        st.session_state["last_updated"] = "Not analyzed yet"

    if "resume_manual" not in st.session_state:
        st.session_state["resume_manual"] = ""
    if "jd_manual" not in st.session_state:
        st.session_state["jd_manual"] = ""

    # ------------------------------------------
    # INPUT SECTION (COLLAPSIBLE)
    # ------------------------------------------
    with st.expander("✏ Input: Paste Resume & Job Description Text", expanded=False):
        col_r, col_j = st.columns(2)
        with col_r:
            st.markdown("#### 👨‍💻 Resume Text")
            resume_text = st.text_area(
                "Paste Resume Content Here:",
                value=st.session_state["resume_manual"],
                height=250,
                key="m2_resume_text",
            )
        with col_j:
            st.markdown("#### 🏢 Job Description Text")
            jd_text = st.text_area(
                "Paste Job Description Content Here:",
                value=st.session_state["jd_manual"],
                height=250,
                key="m2_jd_text",
            )

    # Update session state if changed
    if resume_text != st.session_state["resume_manual"]:
        st.session_state["resume_manual"] = resume_text
    if jd_text != st.session_state["jd_manual"]:
        st.session_state["jd_manual"] = jd_text

    has_any_text = bool(resume_text or jd_text)

    # Extract skills
    tech_resume, soft_resume = ([], [])
    tech_jd, soft_jd = ([], [])

    if resume_text:
        tech_resume, soft_resume = extract_skills(resume_text)
    if jd_text:
        tech_jd, soft_jd = extract_skills(jd_text)

    # Save extracted skills to session state for Milestone 3 pipeline
    st.session_state["m2_extracted_skills"] = {
        "resume": list(set(tech_resume + soft_resume)),
        "jd": list(set(tech_jd + soft_jd)),
    }
    
    # Persist data
    ui_components.save_progress()
    
    # Sets for comparison
    resume_all_skills = set(tech_resume + soft_resume)
    jd_all_skills = set(tech_jd + soft_jd)
    common_skills = sorted(resume_all_skills & jd_all_skills)
    missing_in_resume = sorted(jd_all_skills - resume_all_skills)
    extra_in_resume = sorted(resume_all_skills - jd_all_skills)

    # Update last updated only when analysis has some skills/text
    if has_any_text and (tech_resume or soft_resume or tech_jd or soft_jd):
        st.session_state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        all_selected = []
        tech_selected = []
        soft_selected = []
        conf = {}

        # TABS FOR BETTER ORGANIZATION
        tab_overview, tab_visuals, tab_details = st.tabs(["📊 Overview", "📈 Visualizations", "📋 Detailed Analysis"])

        # --------------------------------------------------
        # TAB 1: OVERVIEW
        # --------------------------------------------------
        with tab_overview:
            # Top row: Left (skills + highlighted text) / Right (chart + metrics)
            left_col, right_col = st.columns([1.4, 1.1])

            with left_col:
                st.markdown("#### 📄 Resume Skills", unsafe_allow_html=True)

                source = st.radio(
                    "Source",
                    options=["Resume", "Job Description"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="source_radio_overview"
                )

                if source == "Resume":
                    src_text = resume_text
                    src_tech = tech_resume
                    src_soft = soft_resume
                    src_name = "Resume"
                else:
                    src_text = jd_text
                    src_tech = tech_jd
                    src_soft = soft_jd
                    src_name = "Job Description"

                all_src_skills = src_tech + src_soft

                st.markdown("##### 🏷 Skill Tags")

                if not src_text:
                    st.info(f"Paste {src_name} text in the input section above to see skills.")
                elif not all_src_skills:
                    st.warning(
                        f"No configured skills were detected in the {src_name.lower()} text."
                    )
                else:
                    conf = skill_confidences(all_src_skills)
                    chips_html = ""

                    for skill in src_tech:
                        score = conf.get(skill, 90)
                        chips_html += f"<span class='skill-chip'>{skill} {score}%</span>"

                    for skill in src_soft:
                        score = conf.get(skill, 88)
                        chips_html += (
                            f"<span class='skill-chip skill-chip-soft'>{skill} {score}%</span>"
                        )

                    st.markdown(chips_html, unsafe_allow_html=True)

                st.markdown("##### ✏ Highlighted Text")

                if src_text:
                    highlighted_html = highlight_text(src_text, all_src_skills)
                    st.markdown(
                        f"<div class='highlight-box'>{highlighted_html}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='highlight-box'>No text available yet. Paste content in the input section to see highlighted skills.</div>",
                        unsafe_allow_html=True,
                    )

                # --------------------------------------------------
                # MOVED SECTIONS: SUMMARY & MARKET INSIGHTS
                # --------------------------------------------------
                if resume_all_skills or jd_all_skills:
                    # Add gap before summary
                    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                    
                    st.markdown("#### 🔍 Resume vs JD Summary", unsafe_allow_html=True)

                    st.markdown(textwrap.dedent(
                        f"""\
                        <div class="summary-strip">
                            <div style="display:flex;flex-wrap:wrap;gap:20px;font-size:1.5rem; align-items:center; justify-content:center;">
                                <div>Overlap: <strong style="color:#10B981; font-size:1.5rem;">{len(common_skills)}</strong> skills</div>
                                <div>Missing: <strong style="color:#EF4444; font-size:1.5rem;">{len(missing_in_resume)}</strong></div>
                                <div>Additional Skills: <strong style="color:#3B82F6; font-size:1.5rem;">{len(extra_in_resume)}</strong></div>
                            </div>
                        </div>
                        """
                    ), unsafe_allow_html=True)

                    if common_skills:
                        st.markdown("*Matching skills*", unsafe_allow_html=True)
                        chips = "".join(
                            [f"<span class='chip-small'>{s}</span>" for s in common_skills]
                        )
                        st.markdown(chips, unsafe_allow_html=True)

                    cols_gap = st.columns(2)
                    with cols_gap[0]:
                        st.markdown(
                            "*Missing in Resume (from JD)*", unsafe_allow_html=True
                        )
                        if missing_in_resume:
                            chips = "".join(
                                [
                                    f"<span class='chip-small chip-missing'>{s}</span>"
                                    for s in missing_in_resume
                                ]
                            )
                            st.markdown(chips, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<span style='font-size:0.8rem;color:var(--muted-color);'>No missing skills detected.</span>",
                                unsafe_allow_html=True,
                            )

                    with cols_gap[1]:
                        st.markdown("*Additional Skills in Resume*", unsafe_allow_html=True)
                        if extra_in_resume:
                            chips = "".join(
                                [
                                    f"<span class='chip-small chip-extra'>{s}</span>"
                                    for s in extra_in_resume
                                ]
                            )
                            st.markdown(chips, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<span style='font-size:0.8rem;color:var(--muted-color);'>No Additional skills detected.</span>",
                                unsafe_allow_html=True,
                            )
                    
            with right_col:
                st.markdown("#### 📊 Skill Distribution")

                if not has_any_text:
                    st.info("Provide Resume and/or Job Description text to view charts.")
                else:
                    tech_selected = src_tech
                    soft_selected = src_soft
                    all_selected = tech_selected + soft_selected

                    tech_count = len(tech_selected)
                    soft_count = len(soft_selected)
                    total_count = tech_count + soft_count

                    conf = skill_confidences(all_selected)
                    avg_conf = round(sum(conf.values()) / len(conf)) if conf else 0

                    if total_count > 0:
                        import charts
                        sizes = [tech_count, soft_count]
                        labels = ["Technical Skills", "Soft Skills"]
                        colors = ["#10b981", "#3b82f6"]
                        
                        fig = charts.get_donut_chart(sizes, labels, colors)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.write("No skills detected yet for a chart.")

                    m1, m2 = st.columns(2, gap="medium")
                    with m1:
                        st.markdown(textwrap.dedent(
                            f"""\
                            <div class="metric-box">
                                <div class="metric-label">Technical Skills</div>
                                <div class="metric-value">{tech_count}</div>
                            </div>
                            """
                        ), unsafe_allow_html=True)
                    with m2:
                        st.markdown(textwrap.dedent(
                            f"""\
                            <div class="metric-box">
                                <div class="metric-label">Soft Skills</div>
                                <div class="metric-value">{soft_count}</div>
                            </div>
                            """
                        ), unsafe_allow_html=True)

                    m3, m4 = st.columns(2, gap="medium")
                    with m3:
                        st.markdown(textwrap.dedent(
                            f"""\
                            <div class="metric-box">
                                <div class="metric-label">Total Skills</div>
                                <div class="metric-value">{total_count}</div>
                            </div>
                            """
                        ), unsafe_allow_html=True)
                    with m4:
                        st.markdown(textwrap.dedent(
                            f"""\
                            <div class="metric-box">
                                <div class="metric-label">Avg. Confidence</div>
                                <div class="metric-value">{avg_conf}%</div>
                            </div>
                            """
                        ), unsafe_allow_html=True)

            
                    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                    st.markdown("#### 🔥 Market Insights (Simulated)")
                    
                    hot_skills = ["Python", "Machine Learning", "React", "AWS", "Docker", "Kubernetes", "TensorFlow", "SQL"]
                    found_hot = [s for s in resume_all_skills if s in hot_skills or s.title() in hot_skills]
                    
                    if found_hot:
                        st.markdown(f"**You possess {len(found_hot)} High-Demand Skills:**")
                        hot_html = ""
                        for s in found_hot:
                            hot_html += f"<span style='background:linear-gradient(45deg, #FF512F, #DD2476); color:white; padding:4px 10px; border-radius:12px; font-size:0.8rem; margin-right:5px; display:inline-block; font-weight:bold;'>🔥 {s}</span>"
                        st.markdown(hot_html, unsafe_allow_html=True)
                    else:
                        st.info("Tip: Consider learning high-demand skills like Python, React, or AWS to boost your profile.")

            st.markdown("---")
            st.markdown(f"#### 🌐 Detected Skills ({source})")
            
            # Show skills only from the selected source (Resume or JD)
            all_unique_skills = sorted(list(set(all_src_skills)))
            
            if not all_unique_skills:
                st.info("No skills detected yet.")
            else:
                # Calculate confidence for all
                all_conf = skill_confidences(all_unique_skills)
                
                # Display in a 2-column grid
                s_col1, s_col2 = st.columns(2)
                
                for i, skill in enumerate(all_unique_skills):
                    score = all_conf.get(skill, 85)
                    is_tech = skill in technical_skills or skill.lower() in technical_skills
                    type_label = "Technical" if is_tech else "Soft Skill"
                    category = get_skill_category(skill)
                    
                    html_row = textwrap.dedent(f"""\
                        <div style="background: rgba(30, 41, 59, 0.4); border-radius: 12px; padding: 15px; border-left: 4px solid #3B82F6; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div style="background: rgba(59, 130, 246, 0.1); width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #3B82F6; font-weight: 800;">{i+1}</div>
                                <div>
                                    <div style="color: #f1f5f9; font-weight: 600; font-size: 1.05rem;">{skill.title()}</div>
                                    <div style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">{get_skill_category(skill)}</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: #60a5fa; font-weight: 700; font-size: 0.9rem;">{score}% CONFIDENCE</div>
                                <div style="width: 80px; height: 4px; background: rgba(59, 130, 246, 0.2); border-radius: 2px; margin-top: 5px;">
                                    <div style="width: {score}%; height: 100%; background: #3B82F6; border-radius: 2px;"></div>
                                </div>
                            </div>
                        </div>
                    """)
                    
                    if i % 2 == 0:
                        with s_col1: st.markdown(html_row, unsafe_allow_html=True)
                    else:
                        with s_col2: st.markdown(html_row, unsafe_allow_html=True)

        # --------------------------------------------------
        # TAB 2: VISUALIZATIONS (NEW FEATURES)
        # --------------------------------------------------
        with tab_visuals:
            if not has_any_text:
                st.info("Please provide text in the input section to generate visualizations.")
            else:
                st.markdown("### 📈 Advanced Skill Analytics")
                
                v_col1, v_col2 = st.columns(2)
                
                # 1. CATEGORY BREAKDOWN (Bar Chart)
                with v_col1:
                    st.markdown("#### Skill Category Breakdown")
                    
                    import pandas as pd
                    import charts
                    cat_counts = Counter()
                    for s in resume_all_skills:
                        cat_counts[get_skill_category(s)] += 1
                    
                    if cat_counts:
                        df_cat = pd.DataFrame.from_dict(cat_counts, orient='index', columns=['Count']).reset_index()
                        df_cat.columns = ['Category', 'Count']
                        
                        fig_bar = charts.get_category_bar_chart(df_cat)
                        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.write("No skills to categorize.")

                # 2. RADAR CHART (Resume vs JD)
                with v_col2:
                    st.markdown("#### Resume vs JD Coverage")
                    
                    # Prepare Radar Data
                    categories = list(skill_categories.keys())
                    resume_cat_counts = {cat: 0 for cat in categories}
                    jd_cat_counts = {cat: 0 for cat in categories}
                    
                    for s in resume_all_skills:
                        cat = get_skill_category(s)
                        if cat in resume_cat_counts: resume_cat_counts[cat] += 1
                        
                    for s in jd_all_skills:
                        cat = get_skill_category(s)
                        if cat in jd_cat_counts: jd_cat_counts[cat] += 1
                        
                    if sum(resume_cat_counts.values()) > 0 or sum(jd_cat_counts.values()) > 0:
                        import charts
                        fig_radar = charts.get_radar_chart(resume_cat_counts, jd_cat_counts)
                        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.write("Not enough data for radar chart.")

                # 3. SKILL FREQUENCY (New Feature)
                st.markdown("#### 🔢 Skill Frequency Analysis")
                freq_col1, freq_col2 = st.columns(2)
                
                with freq_col1:
                    if resume_text and resume_all_skills:
                        r_freq = count_skill_frequency(resume_text, resume_all_skills)
                        df_r_freq = pd.DataFrame.from_dict(r_freq, orient='index', columns=['Count']).sort_values('Count', ascending=False).head(10)
                        st.markdown("**Top Skills in Resume**")
                        st.dataframe(df_r_freq, use_container_width=True)
                
                with freq_col2:
                    if jd_text and jd_all_skills:
                        j_freq = count_skill_frequency(jd_text, jd_all_skills)
                        df_j_freq = pd.DataFrame.from_dict(j_freq, orient='index', columns=['Count']).sort_values('Count', ascending=False).head(10)
                        st.markdown("**Top Skills in JD**")
                        st.dataframe(df_j_freq, use_container_width=True)

                # 4. SKILL ECOSYSTEM (SUNBURST)
                st.markdown("---")
                st.markdown("#### 🌞 Skill Ecosystem (Sunburst)")
                st.markdown(textwrap.dedent(
                    """\
                    This **Sunburst Chart** visualizes the hierarchy of your technical landscape. 
                    - **Inner Circle:** Represents broad Skill Categories (e.g., Languages, Frameworks).
                    - **Outer Ring:** Shows the specific skills you possess within those categories.
                    - **Interaction:** Click on any category to zoom in and explore that specific domain.
                    """
                ))
                
                # Prepare data for Sunburst
                sb_data = []
                total_root_val = 0
                
                for cat, skills in skill_categories.items():
                    # Calculate skills for this category
                    current_cat_skills = []
                    cat_val = 0
                    
                    for skill in skills:
                        if skill in resume_all_skills or skill in jd_all_skills:
                            val = 1 
                            if skill in resume_all_skills and skill in jd_all_skills: val = 2
                            
                            current_cat_skills.append({"id": skill, "parent": cat, "value": val})
                            cat_val += val
                            
                    # Ensure category has at least some value to be visible
                    if cat_val == 0:
                        cat_val = 1  
                        
                    # Add Category Node
                    sb_data.append({"id": cat, "parent": "All Skills", "value": cat_val})
                    total_root_val += cat_val
                    
                    # Add Skill Nodes
                    sb_data.extend(current_cat_skills)

                # Add Root Node
                sb_data.append({"id": "All Skills", "parent": "", "value": total_root_val})
                
                if len(sb_data) > 1:
                    df_sb = pd.DataFrame(sb_data)
                    import charts
                    fig_sb = charts.get_sunburst_overview(df_sb)

                    st.plotly_chart(fig_sb, use_container_width=True)
                else:
                    st.info("Not enough data for Sunburst chart.")

                # 5. SKILL NETWORK (Simulated)
                st.markdown("#### 🕸️ Skill Network Graph")
                st.markdown(textwrap.dedent("This graph visualizes how your skills connect to broader technical domains. **Central Node:** You. **Blue Nodes:** Categories. **Green/Red Nodes:** Skills (Green = Present, Red = Missing)."))
                
                if resume_all_skills:
                    # Simple node-link simulation
                    edge_x = []
                    edge_y = []
                    node_x = []
                    node_y = []
                    node_text = []
                    node_color = []
                    
                    # Center node
                    node_x.append(0)
                    node_y.append(0)
                    node_text.append("YOU")
                    node_color.append("#ffffff")
                    
                    import math
                    
                    # Category nodes
                    cats = list(skill_categories.keys())
                    n_cats = len(cats)
                    radius_cat = 1
                    
                    cat_coords = {}
                    
                    for i, cat in enumerate(cats):
                        angle = (2 * math.pi * i) / n_cats
                        cx = radius_cat * math.cos(angle)
                        cy = radius_cat * math.sin(angle)
                        cat_coords[cat] = (cx, cy)
                        
                        # Add Cat Node
                        node_x.append(cx)
                        node_y.append(cy)
                        node_text.append(cat)
                        node_color.append("#3B82F6")
                        
                        # Edge from Center to Cat
                        edge_x.extend([0, cx, None])
                        edge_y.extend([0, cy, None])
                        
                        # Skill Nodes attached to Cat
                        relevant_skills = [s for s in (resume_all_skills | jd_all_skills) if get_skill_category(s) == cat]
                        n_skills = len(relevant_skills)
                        radius_skill = 1.5  
                        
                        for j, skill in enumerate(relevant_skills):
                            # Spread skills in a wider arc
                            s_angle = angle + ((j - n_skills/2) * 0.3)
                            sx = cx + radius_skill * math.cos(s_angle)
                            sy = cy + radius_skill * math.sin(s_angle)
                            
                            node_x.append(sx)
                            node_y.append(sy)
                            node_text.append(skill)
                            node_color.append("#10B981" if skill in resume_all_skills else "#EF4444")
                            
                            # Edge from Cat to Skill
                            edge_x.extend([cx, sx, None])
                            edge_y.extend([cy, sy, None])

                    import charts
                    fig_net = charts.get_network_graph(edge_x, edge_y, node_x, node_y, node_text, node_color)
                    st.plotly_chart(fig_net, use_container_width=True)
                else:
                    st.info("Add skills to view the network.")

        # --------------------------------------------------
        # TAB 3: DETAILED ANALYSIS & EXPORT
        # --------------------------------------------------
        with tab_details:
            st.markdown("#### 📋 Comprehensive Skill List (Resume & JD)")
            
            # Filter Controls
            c_filter1, c_filter2 = st.columns(2)
            with c_filter1:
                filter_type = st.selectbox("Filter by Type", ["All Skills", "Technical Only", "Soft Skills Only", "Missing Skills"])
            with c_filter2:
                sort_by = st.selectbox("Sort by", ["Confidence (High to Low)", "Name (A-Z)"])

            # Combine all skills for detailed view
            combined_skills = sorted(list(resume_all_skills | jd_all_skills))
            
            # Apply Filters
            if filter_type == "Technical Only":
                combined_skills = [s for s in combined_skills if s in technical_skills or s.lower() in technical_skills]
            elif filter_type == "Soft Skills Only":
                combined_skills = [s for s in combined_skills if s in soft_skills or s.lower() in soft_skills]
            elif filter_type == "Missing Skills":
                combined_skills = [s for s in combined_skills if s in missing_in_resume]

            # Calculate confidence for the combined list
            combined_conf = skill_confidences(combined_skills)
            
            # Apply Sort
            if sort_by == "Confidence (High to Low)":
                combined_skills.sort(key=lambda x: combined_conf.get(x, 0), reverse=True)
            else:
                combined_skills.sort()

            if not combined_skills:
                st.write("No skills match the selected filters.")
            else:
                # Export Button
                export_data = {
                    "resume_skills": list(resume_all_skills),
                    "jd_skills": list(jd_all_skills),
                    "missing_skills": list(missing_in_resume),
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                json_str = json.dumps(export_data, indent=2)
                
                col_exp1, col_exp2 = st.columns([3, 1])
                with col_exp2:
                    st.download_button(
                        label="📥 Export Skills (JSON)",
                        data=json_str,
                        file_name="extracted_skills.json",
                        mime="application/json"
                    )

                for skill in combined_skills:
                    score = combined_conf.get(skill, 85)
                    is_tech = skill in tech_selected
                    type_label = "Technical Skill" if is_tech else "Soft Skill"
                    category = get_skill_category(skill)

                    st.markdown(textwrap.dedent(f"""\
                        <div class="detail-row">
                          <div class="detail-info">
                            <div class="detail-title">{skill}</div>
                            <div class="detail-subtitle">{type_label} &bull; {category}</div>
                          </div>
                          <div class="skill-bar" style="width: 150px; margin-right: 15px; background:rgba(255,255,255,0.1); border-radius:10px; height:8px; overflow:hidden;">
                            <div class="skill-bar-fill" style="width:{score}%; background:var(--accent-color); height:100%; border-radius:10px;"></div>
                          </div>
                          <div class="detail-score">{score}%</div>
                        </div>
                    """), unsafe_allow_html=True)

    # ------------------------------------------
    # NAVIGATION BUTTONS
    # ------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    
    from components import navigate_to

    def proceed_to_m3():
        if "m2_extracted_skills" in st.session_state:
            data = st.session_state["m2_extracted_skills"]
            r_s = data.get("resume", [])
            j_s = data.get("jd", [])
            
            if r_s and j_s:
                # Compute heavy matrix
                from milestone3 import compute_similarity
                df_plot, details, stats = compute_similarity(r_s, j_s)
                
                # Store in M3 expected format
                st.session_state["m3_results"] = {
                    "matrix_df": df_plot, 
                    "jd_details": details, 
                    "stats": stats,
                    "resume_skills": r_s, 
                    "jd_skills": j_s, 
                    "critical_skills": []
                }
        
        # Navigate
        navigate_to("Milestone 3: Gap Analysis")

    with col_nav1:
        st.button("⬅ Back to Milestone 1", type="primary", on_click=navigate_to, args=("Milestone 1: Data Ingestion",))
            
    with col_nav3:
        # Proceed with pre-computation callback
        st.button("Proceed to Milestone 3 ➡", type="primary", on_click=proceed_to_m3)

    # -------------------------
    # FOOTER BAR
    # -------------------------
    components.render_footer()


if __name__ == "__main__":
    st.set_page_config(
        page_title="SkillGapAI — Milestone 2",
        page_icon="🧭",
        layout="wide",
    )
    app()
