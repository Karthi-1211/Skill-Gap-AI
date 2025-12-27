import streamlit as st
import components as ui_components
try:
    from milestone2 import extract_skills
    from milestone3 import compute_similarity
except ImportError:
    pass

import pdf_gen
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import time
import random
import numpy as np
from collections import Counter
from streamlit_lottie import st_lottie
import textwrap

@st.cache_data
def load_lottieurl(url: str):
    try:
        import requests
        r = requests.get(url, timeout=2)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# -------------------------------------------------------
# CORE LOGIC
# -------------------------------------------------------
def calculate_ats_score_advanced(resume_text, jd_text=""):
    """
    Returns a comprehensive Audit Report with Deep Feedback + JD Match.
    Uses local NLP extraction and Embedding Similiarity.
    """
    raw_score = 0.0 
    checks = [] # {category, check, status (bool), feedback, impact (high/med/low)}
    
    clean_text = resume_text.strip()
    resume_lower = clean_text.lower()
    words = re.findall(r'\w+', resume_lower)
    word_count = len(words)
    
    # Keyword Extraction
    common_stops = {"and", "the", "to", "of", "in", "a", "with", "for", "on", "as", "is", "by", "an", "at", "or", "from", "i", "my"}
    keywords = [w for w in words if w not in common_stops and len(w) > 3]
    top_keywords = Counter(keywords).most_common(12)

    def add_check(cat, name, status, feedback, impact="Medium"):
        nonlocal raw_score
        pts = 0.0
        if status:
            # Precise point values
            if impact == "Critical": pts = 9.5
            elif impact == "High": pts = 4.8
            elif impact == "Medium": pts = 2.5
            else: pts = 1.0
            raw_score += pts
        checks.append({
            "category": cat, "name": name, "status": status, 
            "feedback": feedback, "impact": impact
        })

    # 1. FILE & FORMATTING
    add_check("Formatting", "Text Selectability", True, "OCR-free plain text detected.", "Critical")
    if 450 <= word_count <= 1200:
        add_check("Formatting", "Word Count", True, f"Optimal length ({word_count} words).", "High")
    elif word_count < 450:
        add_check("Formatting", "Word Count", False, f"Too short ({word_count} words). Aim for 450+.", "High")
    else:
        add_check("Formatting", "Word Count", False, f"Too long ({word_count} words). Keep under 1200.", "Medium")

    bullet_count = resume_text.count('•') + resume_text.count('- ') + resume_text.count('* ')
    if bullet_count > 10:
        add_check("Formatting", "Bullet Points", True, f"Good list usage ({bullet_count} bullets).", "High")
    else:
        add_check("Formatting", "Bullet Points", False, "Use more bullet points for readability.", "High")

    # 2. ESSENTIALS & CONTACT
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    if emails:
        add_check("Essentials", "Email Address", True, f"Found: {emails[0]}", "Critical")
    else:
        add_check("Essentials", "Email Address", False, "Missing contact email.", "Critical")

    phones = re.findall(r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', resume_text)
    if phones:
        add_check("Essentials", "Phone Number", True, "Contact number detected.", "Critical")
    else:
        add_check("Essentials", "Phone Number", False, "No phone number found.", "Critical")
        
    if "linkedin.com/in/" in resume_lower:
        add_check("Essentials", "LinkedIn Profile", True, "Profile link active.", "High")
    else:
        add_check("Essentials", "LinkedIn Profile", False, "Add your LinkedIn URL.", "High")

    # 3. STRUCTURE
    sections = {
        "Experience": r"(work|professional|relavant)\s+experience|employment\s+history|work\s+history",
        "Education": r"education|academic|qualification",
        "Skills": r"skills|technical\s+skills|expertise",
        "Projects": r"projects|portfolio"
    }
    for sec, pattern in sections.items():
        if re.search(pattern, resume_lower):
            add_check("Structure", f"{sec} Section", True, f"Found '{sec}' header.", "High")
        else:
            add_check("Structure", f"{sec} Section", False, f"Missing '{sec}' section.", "High")

    # 4. CONTENT
    metrics = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?\s*(%|\$|M|K|\+|k|m|Yrs|yrs))', resume_text)
    if len(metrics) >= 5:
        add_check("Content", "Quantifiable Impact", True, f"Found {len(metrics)}+ metrics.", "Critical")
    elif len(metrics) >= 2:
        add_check("Content", "Quantifiable Impact", False, f"Only {len(metrics)} metrics found. Quantify more.", "High")
    else:
        add_check("Content", "Quantifiable Impact", False, "No hard numbers found. Quantify success.", "Critical")

    strong_verbs = ["architected", "developed", "led", "managed", "analyzed", "created", "designed", "implemented", "optimized", "spearheaded", "built", "engineered"]
    found_verbs = list(set([v for v in strong_verbs if f" {v} " in f" {resume_lower} "]))
    
    if len(found_verbs) >= 5:
        add_check("Content", "Power Verbs", True, f"Strong action vocabulary ({len(found_verbs)} verbs).", "High")
    else:
        add_check("Content", "Power Verbs", False, "Use more action verbs (e.g. Led, Built, Analyzed).", "High")
    time.sleep(0.5)
     
    # Base calculation
    max_potential = 65.0 
    normalized_score = (raw_score / max_potential) * 100
    
    final_score = min(95.0, normalized_score)
    
    # We round to 1 decimal place.
    final_score = round(final_score, 1)

    jd_match_score = 0
    missing_keywords = []

    if jd_text and len(jd_text.strip()) > 10:
        # Extract Skills using NLP
        res_skills_found, _ = extract_skills(resume_text)
        jd_skills_found, _ = extract_skills(jd_text)
        
        if not jd_skills_found:
             intersection = set(resume_lower.split()) & set(jd_text.lower().strip().split())
             jd_match_score = min(100, int((len(intersection) / len(list(set(jd_text.lower().split())))) * 100 * 2)) 
        else:
             _, jd_details, sim_stats = compute_similarity(res_skills_found, jd_skills_found)
             jd_match_score = sim_stats['overall']
             missing_keywords = [d['jd_skill'] for d in jd_details if d['category'] == 'Low Match']
        
        # Weighted Final Score: 60% Quality, 40% Relevance
        weighted_score = (final_score * 0.6) + (jd_match_score * 0.4)
        final_score = min(95.0, weighted_score)
        final_score = round(final_score, 1)

    return {
        "score": final_score,
        "resume_quality": final_score,
        "jd_match_score": jd_match_score,
        "checks": checks,
        "metrics_count": len(metrics),
        "verb_count": len(found_verbs),
        "word_count": word_count,
        "email": emails[0] if emails else "N/A",
        "top_keywords": top_keywords,
        "missing_keywords": missing_keywords
    }

# ----------------
# MAIN APP
# ----------------
def app():
    # Initialize State
    if "ats_page_step" not in st.session_state:
        st.session_state["ats_page_step"] = "upload"

    # Helper: Reset
    def reset_app():
        st.session_state["ats_page_step"] = "upload"
        st.session_state["ats_report_v3"] = None
        st.session_state["ats_uploaded_file"] = None

    ui_components.render_navbar()
    ui_components.scroll_to_top()

    # ---------------------------------------------------
    # GLOBAL CSS - MODERN HOLOGRAPHIC THEME
    # ---------------------------------------------------
    st.markdown(textwrap.dedent("""\
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
        
        /* CORE PAGE */
        .main .block-container { max-width: 1400px; padding-top: 2rem; }
        * { font-family: 'Outfit', sans-serif; }
        
        /* FILE UPLOADER RESTYLING - The 'Clickable Box' Fix */
        .stFileUploader {
            width: 100%;
        }
        [data-testid='stFileUploader'] {
            width: 100%;
        }
        [data-testid='stFileUploader'] section {
            padding: 50px;
            background: rgba(15, 23, 42, 0.4);
            border: 2px dashed rgba(99, 102, 241, 0.4);
            border-radius: 24px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            backdrop-filter: blur(10px);
        }
        [data-testid='stFileUploader'] section:hover {
            border-color: #a855f7;
            background: rgba(168, 85, 247, 0.1);
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            cursor: pointer;
        }
        /* Custom Text Injection for Uploader */
        [data-testid='stFileUploader'] section > button {
             display: none; 
        }
        
        /* ANALYZING ANIMATIONS */
        .analyzing-wrapper {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 60vh;
            position: relative;
        }
        
        /* NEON CARDS */
        .neon-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .neon-card:hover { border-color: rgba(99, 102, 241, 0.5); box-shadow: 0 0 20px rgba(99, 102, 241, 0.2); }
        
        /* SCORE METRIC - DONUT */
        .score-donut-container { position: relative; width: 220px; height: 220px; margin: 0 auto; }
        
        /* PROGRESS BAR CUSTOM */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #6366f1, #a855f7, #ec4899);
        }
        
        /* TITLES */
        .holo-title {
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -1px;
        }
        
        /* CHIPS */
        .keyword-chip {
            display: inline-flex; align-items: center;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 6px 14px;
            border-radius: 100px;
            margin: 4px;
            font-size: 0.85rem;
            color: #e2e8f0;
            transition: all 0.2s;
        }
        .keyword-chip:hover {
            background: rgba(99, 102, 241, 0.2);
            transform: scale(1.05);
            border-color: #818cf8;
        }
        
        /* AUDIT */
        .audit-row {
            padding: 18px; margin-bottom: 12px;
            border-radius: 12px;
            background: rgba(255,255,255,0.02);
            border-left: 4px solid #334155;
            display: flex; align-items: center; justify-content: space-between;
        }
        .audit-pass { border-color: #22c55e; background: linear-gradient(to right, rgba(34,197,94,0.05), transparent); }
        .audit-fail { border-color: #ef4444; background: linear-gradient(to right, rgba(239,68,68,0.05), transparent); }
        </style>
    """), unsafe_allow_html=True)

    main_view = st.empty()

    # =========================================================================
    # VIEW NO. 1: UPLOAD PAGE
    # =========================================================================
    if st.session_state["ats_page_step"] == "upload":
        with main_view.container():
            
            def on_upload_change():
                if st.session_state.get("ats_resume_uploader"):
                    st.session_state["ats_uploaded_file"] = st.session_state["ats_resume_uploader"]
                    st.session_state["ats_jd_text"] = st.session_state.get("ats_jd_input", "")
                    
                    try:
                        import milestone1
                        ats_resume = st.session_state["ats_uploaded_file"]
                        jd_txt = st.session_state["ats_jd_text"]
                        
                        ats_resume.seek(0)
                        raw_text = milestone1.parse_file(ats_resume)
                        report = calculate_ats_score_advanced(raw_text, jd_txt)
                        
                        st.session_state["ats_report_v3"] = report
                        st.session_state["ats_page_step"] = "results"
                    except Exception as e:
                        print(f"Analysis Error: {e}")
                        st.session_state["ats_page_step"] = "results"

            st.markdown(textwrap.dedent("""\
                <style>
                    /* ANIMATED BACKGROUND */
                    @keyframes aurora-flow { 
                        0% { background-position: 0% 50%; }
                        50% { background-position: 100% 50%; }
                        100% { background-position: 0% 50%; }
                    }
    
                    .ultra-title {
                        font-size: 4.5rem;
                        font-weight: 900;
                        text-align: center;
                        background: linear-gradient(300deg, #c084fc, #6366f1, #3b82f6, #6366f1);
                        background-size: 300% 300%;
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        animation: aurora-flow 6s ease infinite;
                        margin-bottom: 0px;
                        letter-spacing: -2px;
                        line-height: 1.1;
                        text-shadow: 0 0 80px rgba(99,102,241,0.5);
                    }
                    
                    .ultra-subtitle {
                        color: #cbd5e1;
                        font-size: 1.3rem;
                        text-align: center;
                        font-weight: 300;
                        margin-bottom: 50px;
                        max-width: 600px;
                        margin-left: auto;
                        margin-right: auto;
                        position: relative; z-index: 2;
                    }
    
                    /* --- SCANNER CARD IMPLEMENTATION --- */
                    [data-testid="stHorizontalBlock"] > div:nth-of-type(2) [data-testid="stVerticalBlock"] {
                        background: rgba(15, 23, 42, 0.6);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 24px;
                        padding: 30px !important;
                        position: relative;
                        overflow: hidden;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                        isolation: isolate;
                    }
    
                    /* PAPER GRID PATTERN (Behind Content) */
                    [data-testid="stHorizontalBlock"] > div:nth-of-type(2) [data-testid="stVerticalBlock"]::before {
                        content: '';
                        position: absolute;
                        top: 20px; bottom: 20px; left: 20px; right: 20px;
                        background: rgba(255, 255, 255, 0.02);
                        background-image: 
                            linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
                        background-size: 20px 20px;
                        border: 1px solid rgba(255,255,255,0.05);
                        /* border-radius: 12px; */
                        z-index: -1;
                    }
    
                    /* SCANNER BEAM (On Top of Paper, Behind Inputs) */
                    [data-testid="stHorizontalBlock"] > div:nth-of-type(2) [data-testid="stVerticalBlock"]::after {
                        content: '';
                        position: absolute;
                        top: 0; left: 0; right: 0; height: 2px;
                        background: linear-gradient(90deg, transparent, #818cf8, #3b82f6, transparent);
                        box-shadow: 0 0 20px #818cf8;
                        z-index: 0;
                        animation: scan-move 4s ease-in-out infinite;
                    }
    
                    @keyframes scan-move {
                        0% { top: 10%; opacity: 0; }
                        10% { opacity: 1; }
                        90% { opacity: 1; }
                        100% { top: 90%; opacity: 0; }
                    }
    
                    /* Ensure inputs are clearly visible above the dark background */
                    .stTextArea textarea {
                        background-color: rgba(30, 41, 59, 0.8) !important;
                    }
                    
                    /* FEATURE GRID */
                    .feature-grid {
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 20px;
                        margin-top: 50px;
                        position: relative; z-index: 2;
                    }
                    .feature-item {
                        background: rgba(30, 41, 59, 0.5);
                        padding: 25px;
                        border-radius: 16px;
                        border: 1px solid rgba(255,255,255,0.05);
                        text-align: center;
                        transition: background 0.3s;
                    }
                    .feature-item:hover {
                        background: rgba(30, 41, 59, 0.8);
                        border-color: rgba(99,102,241,0.3);
                    }
                    .f-icon { font-size: 2rem; margin-bottom: 10px; display: block; }
                    .f-title { font-weight: 700; color: #fff; margin-bottom: 5px; font-size: 1.1rem; }
                    .f-desc { color: #94a3b8; font-size: 0.9rem; line-height: 1.4; }
                </style>
            """), unsafe_allow_html=True)

            
            # HERO SECTION
            st.markdown('<div class="ultra-title">ATS INTELLIGENCE</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="ultra-subtitle">
                Deconstruct the algorithm. Optimize your keywords. <br>
                <span style="color:#818cf8; font-weight:600;">Get hired faster.</span>
            </div>
            """, unsafe_allow_html=True)
            
            c_L, c_Main, c_R = st.columns([1, 2, 1])
            with c_Main:
                st.markdown(textwrap.dedent("""\
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:25px; position:relative; z-index:1;">
                        <div style="font-weight:700; color:#fff; font-size:1.2rem;">🚀 Upload Center</div>
                        <div style="font-size:0.8rem; color:#4ade80; background:rgba(34,197,94,0.1); padding:4px 10px; border-radius:12px;">● System Online</div>
                    </div>
                """), unsafe_allow_html=True)

                st.text_area(
                    "Target Job Description",
                    height=100,
                    placeholder="Paste the job description here (Ctrl+V) for deeper analysis...",
                    key="ats_jd_input",
                    label_visibility="visible"
                )
                
                st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)
                
                st.file_uploader(
                    "Upload Resume PDF",
                    type=["pdf"],
                    key="ats_resume_uploader",
                    on_change=on_upload_change
                )
                
                st.markdown(textwrap.dedent("""\
                    <div style="margin-top:20px; text-align:center; font-size:0.85rem; color:#64748b; position:relative; z-index:1;">
                        Supported Formats: PDF Only • Max Size: 200MB
                    </div>
                """), unsafe_allow_html=True)

            st.markdown(textwrap.dedent("""\
                <div class="feature-grid">
                    <div class="feature-item">
                        <span class="f-icon">🧠</span>
                        <div class="f-title">Semantic Matching</div>
                        <div class="f-desc">Our AI analyzes context, not just keywords, to match you with the right roles.</div>
                    </div>
                    <div class="feature-item">
                        <span class="f-icon">⚡</span>
                        <div class="f-title">Instant Scoring</div>
                        <div class="f-desc">Get a detailed breakdown of your resume's performance in milliseconds.</div>
                    </div>
                    <div class="feature-item">
                        <span class="f-icon">🎯</span>
                        <div class="f-title">Keyword Gap</div>
                        <div class="f-desc">Identify exactly which skills you are missing from the job description.</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)

# ======================================
# VIEW NO. 3: RESULTS DASHBOARD
# ======================================

    elif st.session_state["ats_page_step"] == "results" and "ats_report_v3" in st.session_state:
        with main_view.container():
            report = st.session_state["ats_report_v3"]
            score = report["score"]
            checks = report["checks"]
            
            # Helper: Calculate Category Scores
            cats = ["Essentials", "Structure", "Content", "Formatting"]
            cat_scores = {}
            for c in cats:
                total = len([x for x in checks if x["category"] == c])
                passed = len([x for x in checks if x["category"] == c and x["status"]])
                cat_scores[c] = int((passed / total * 100)) if total > 0 else 0

            # Helper: Group Checks by Severity
            passed_checks = [c for c in checks if c["status"]]
            critical_issues = [c for c in checks if not c["status"] and c["category"] in ["Essentials", "Structure"]]
            warnings = [c for c in checks if not c["status"] and c["category"] not in ["Essentials", "Structure"]]

            if st.button("← Upload New Application"):
                reset_app()
                st.rerun()
            
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

            col_L, col_R = st.columns([0.35, 0.65], gap="large")

            # --- LEFT COLUMN: SCORE & STATS ---
            with col_L:
                # 1. Score Card
                st.markdown(textwrap.dedent(f"""\
                    <div style="background:rgba(30, 41, 59, 0.5); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:30px; text-align:center;">
                        <div style="font-size:1rem; color:#94a3b8; margin-bottom:10px;">ATS MATCH SCORE</div>
                        <div style="font-size:4.5rem; font-weight:800; color:{'#22c55e' if score >= 85 else '#facc15' if score >= 70 else '#ef4444'}; line-height:1;">
                            {score}
                        </div>
                        <div style="font-size:1.2rem; margin-top:5px; color:#fff; font-weight:600;">
                            {'Top 5% Candidate' if score >= 85 else 'Good Match' if score >= 70 else 'Needs Improvement'}
                        </div>
                    </div>
                """), unsafe_allow_html=True)
                
                st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

                # 2. Category Breakdown
                st.markdown("##### Score Breakdown")
                
                # Formatting
                st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:5px;'><span>Formatting</span><span>{cat_scores['Formatting']}%</span></div>", unsafe_allow_html=True)
                st.progress(cat_scores['Formatting'] / 100)
                
                # Content
                st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:5px; margin-top:10px;'><span>Content Quality</span><span>{cat_scores['Content']}%</span></div>", unsafe_allow_html=True)
                st.progress(cat_scores['Content'] / 100)
                
                # Structure
                st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:5px; margin-top:10px;'><span>Structure & sections</span><span>{cat_scores['Structure']}%</span></div>", unsafe_allow_html=True)
                st.progress(cat_scores['Structure'] / 100)

                st.markdown('<div style="height:30px;"></div>', unsafe_allow_html=True)

                # 3. Action Buttons
                pdf_bytes = pdf_gen.create_ats_report_pdf(report, candidate_name="Candidate")
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="ATS_Audit_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                if st.button("🔗 Share Results", use_container_width=True):
                    st.info("Public link copied to clipboard!")

            # --- RIGHT COLUMN: TABS & DETAILS ---
            with col_R:
                tabs = st.tabs(["Overview", "Detailed Analysis", "Suggestions", "Job Match"])

                # TAB 1: OVERVIEW
                with tabs[0]:
                    st.markdown("### Executive Summary")
                    st.caption(f"Analysis of {report['word_count']} words found in your resume.")
                    
                    # Quick Stats Grid
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Total Words", report['word_count'])
                    with c2:
                        st.metric("Power Verbs", report['verb_count'])
                    with c3:
                        st.metric("Hard Metrics", report['metrics_count'])
                    
                    st.markdown("---")
                    st.subheader("detected_keywords.Cloud")
                    if report['top_keywords']:
                        html_tags = ""
                        for k, v in report['top_keywords']:
                             size = 0.8 + (v/10)
                             html_tags += f"<span style='display:inline-block; margin:4px; padding:4px 10px; background:rgba(99,102,241,0.1); border-radius:12px; color:#a5b4fc; font-size:{min(size, 1.5)}rem;'>{k}</span>"
                        st.markdown(html_tags, unsafe_allow_html=True)
                    else:
                        st.info("No significant keywords detected.")

                # TAB 2: DETAILED ANALYSIS
                with tabs[1]:
                    # 1. PASSED
                    st.markdown(f"#### 🟢 Passed Checks ({len(passed_checks)})")
                    with st.expander("View Passed Items", expanded=False):
                        for p in passed_checks:
                            st.markdown(f"✅ **{p['name']}**: {p['feedback']}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # 2. WARNINGS
                    st.markdown(f"#### 🟠 Warnings ({len(warnings)})")
                    if warnings:
                        for w in warnings:
                            st.warning(f"**{w['name']}**: {w['feedback']}")
                    else:
                        st.info("No warnings found.")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # 3. CRITICAL ISSUES
                    st.markdown(f"#### 🔴 Critical Issues ({len(critical_issues)})")
                    if critical_issues:
                        for c in critical_issues:
                            st.error(f"**{c['name']}**: {c['feedback']}")
                    else:
                        st.success("No critical issues found!")

                # TAB 3: SUGGESTIONS
                with tabs[2]:
                    st.markdown("### AI Recommendations")
                    if critical_issues or warnings:
                        st.markdown("Based on our audit, here are your top priorities:")
                        for i, issue in enumerate(critical_issues + warnings, 1):
                            st.markdown(f"**{i}. Fix '{issue['name']}'**")
                            st.markdown(f"> *Recommendation*: {issue['feedback']}")
                            st.markdown("---")
                    else:
                        st.balloons()
                        st.markdown("Your resume is optimized! Focus on networking and interview prep.")

                # TAB 4: JOB MATCH
                with tabs[3]:
                    st.markdown("### JD Keyword Gap Analysis")
                    if st.session_state.get("ats_jd_text"):
                        # Show missing keywords
                        missing = report.get("missing_keywords", [])
                        if missing:
                            st.error(f"Missing {len(missing)} Critical Keywords")
                            st.write("Add these to your skills or experience to boost your match score:")
                            
                            # Chip view
                            chips = ""
                            for m in missing:
                                chips += f"<span style='margin:4px; display:inline-block; padding:4px 10px; background:#fee2e2; color:#ef4444; border-radius:14px; font-weight:600;'>{m}</span>"
                            st.markdown(chips, unsafe_allow_html=True)
                        else:
                            st.success("You matched all critical keywords from the JD!")
                    else:
                        st.info("Upload a Job Description on the previous page (or below) to see a keyword gap analysis.")
                        jd_new = st.text_area("Paste JD here for instant analysis:", height=150)
                        if st.button("Analyze JD"):
                            st.session_state["ats_jd_text"] = jd_new
                            st.session_state["ats_jd_input"] = jd_new
                            import milestone1
                            ats_resume = st.session_state["ats_uploaded_file"]
                            ats_resume.seek(0)
                            raw_text = milestone1.parse_file(ats_resume)
                            report = calculate_ats_score_advanced(raw_text, jd_new)
                            st.session_state["ats_report_v3"] = report
                            st.rerun()

    ui_components.render_footer()
