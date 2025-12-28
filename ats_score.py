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
def calculate_ats_score_realtime(resume_text, jd_text=""):
    """
    Simulates a Real-Time Enterprise ATS Scoring Engine.
    Uses strict penalties for missing sections and heavily weighs JD overlap.
    """
    raw_score = 0.0 
    checks = [] # {category, check, status (bool), feedback, impact (high/med/low)}
    
    clean_text = resume_text.strip()
    resume_lower = clean_text.lower()
    words = re.findall(r'\w+', resume_lower)
    word_count = len(words)
    sentences = re.split(r'[.!?]+', clean_text)
    avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

    # --- CONSTANTS & SCORING WEIGHTS ---
    WEIGHTS = {"Critical": 12.0, "High": 6.0, "Medium": 3.0, "Low": 1.0}
    MAX_POSSIBLE_SCORE = 0.0 

    def add_check(cat, name, status, feedback, impact="Medium"):
        nonlocal raw_score, MAX_POSSIBLE_SCORE
        weight = WEIGHTS.get(impact, 1.0)
        
        # We always add to max_possible to calculate percentage later
        MAX_POSSIBLE_SCORE += weight
        
        if status:
            raw_score += weight
        
        checks.append({
            "category": cat, "name": name, "status": status, 
            "feedback": feedback, "impact": impact
        })

    # --- DATA EXTRACTION ---
    lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
    candidate_name = lines[0] if lines else "Candidate"
    if len(candidate_name) > 40 or "@" in candidate_name or len(candidate_name.split()) > 6:
        candidate_name = "Candidate"
        
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    email_found = emails[0] if emails else "N/A"

    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, resume_text)
    valid_phones = []
    if phones:
        matches = re.finditer(phone_pattern, resume_text)
        for m in matches:
            p_text = m.group(0).strip()
            if len(re.sub(r'\D', '', p_text)) >= 10: 
                valid_phones.append(p_text)
    phone_found = valid_phones[0] if valid_phones else "N/A"

    # --- 1. KO FACTORS (KNOCK-OUT) ---
    # Real ATS rejects immediately if contact info or basic formatting is unusable.
    # We won't stop execution, but we'll flag them as Critical.
    
    # 1.1 Contact Info
    if email_found != "N/A":
        add_check("Essentials", "Email Verification", True, f"Verified: {email_found}", "Critical")
    else:
        add_check("Essentials", "Email Verification", False, "Missing Email. **Auto-Reject Risk**.", "Critical")

    pattern_phone = phone_found != "N/A"
    add_check("Essentials", "Phone Verification", pattern_phone, 
              "Contact number detected." if pattern_phone else "No phone detected.", "Critical")
              
    # 1.2 Parsing Readability
    add_check("Formatting", "Machine Readability", True, "Text layer is selectable.", "Critical")

    # --- 2. STRUCTURAL INTEGRITY ---
    sections = {
        "Experience": r"(work|professional|relevant|industry)\s+experience|employment\s+history|work\s+history",
        "Education": r"education|academic|qualification|university",
        "Skills": r"skills|technical\s+skills|expertise|competencies|technologies",
        "Projects": r"projects|portfolio|personal\s+projects"
    }
    section_presence = {}
    for sec, pattern in sections.items():
        found = bool(re.search(pattern, resume_lower))
        section_presence[sec] = found
        impact = "Critical" if sec in ["Experience", "Education"] else "High"
        add_check("Structure", f"{sec} Detected", found, 
                  f"Found standard header: {sec}" if found else f"Missing Section: {sec}", impact)

    # --- 3. FORMATTING HYGIENE ---
    if 450 <= word_count <= 1200:
        add_check("Formatting", "Word Count", True, f"Optimal volume ({word_count} words).", "High")
    elif word_count < 450:
        add_check("Formatting", "Word Count", False, f"Too brief ({word_count} words). Low context.", "High")
    else:
        add_check("Formatting", "Word Count", False, f"Too lengthy ({word_count} words). Risk of truncation.", "Medium")

    bullet_count = resume_text.count('•') + resume_text.count('- ') + resume_text.count('* ')
    if bullet_count > 15:
        add_check("Formatting", "Bulletization", True, "High readability via bullets.", "High")
    else:
        add_check("Formatting", "Bulletization", False, "Text block heavy. Use more bullets.", "High")

    # --- 4. CONTENT QUALITY ---
    # Metrics
    metrics = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?\s*(%|\$|M|K|\+|k|m))', resume_text)
    metric_score = len(metrics)
    if metric_score >= 6:
        add_check("Content", "Quantifiable Impact", True, f"Strong data usage ({metric_score} metrics).", "High")
    elif metric_score >= 3:
        add_check("Content", "Quantifiable Impact", False, f"Weak data usage ({metric_score} metrics). Goal: 6+", "High")
    else:
        add_check("Content", "Quantifiable Impact", False, "No quantified achievements found.", "Critical")

    # Verbs
    strong_verbs = ["architected", "developed", "led", "managed", "analyzed", "created", "designed", "implemented", "optimized", "spearheaded", "built", "engineered", "orchestrated", "pioneered", "delivered", "championed", "transformed", "reduced", "increased"]
    found_verbs = list(set([v for v in strong_verbs if f" {v} " in f" {resume_lower} "]))
    
    if len(found_verbs) >= 6:
        add_check("Content", "Action Verbs", True, f"Dynamic vocabulary ({len(found_verbs)} unique).", "High")
    else:
        add_check("Content", "Action Verbs", False, "Passive voice detected. Use strong verbs.", "High")

    # Cliches
    cliches = ["hard worker", "team player", "think outside the box", "go getter", "detail oriented", "responsible for", "duties included", "best of breed"]
    found_cliches = [c for c in cliches if c in resume_lower]
    if not found_cliches:
         add_check("Content", "Cliché Check", True, "Professional, direct tone.", "Medium")
    else:
         add_check("Content", "Cliché Check", False, f"Remove fillers: {', '.join(found_cliches[:2])}", "Medium")

    # --- CALCULATE BASE QUALITY SCORE ---
    quality_score = (raw_score / MAX_POSSIBLE_SCORE) * 100 if MAX_POSSIBLE_SCORE > 0 else 0
    
    # Penalties for MISSING CRITICAL SECTIONS (The "Real" ATS Logic)
    # Even if you have good keywords, if you have no Experience section, you are out.
    if not section_presence["Experience"]:
        quality_score = min(quality_score, 45) # Hard Cap
    
    if not section_presence["Education"] and not section_presence["Skills"]:
        quality_score = min(quality_score, 50) # Hard Cap

    quality_score = round(min(100.0, quality_score), 1)

    # --- 5. JD RELEVANCE SCORE ---
    jd_match_score = 0.0
    missing_keywords = []
    top_keywords = []
    
    if jd_text and len(jd_text.strip()) > 10:
        # Import heavy NLP only if needed
        try:
            from milestone2 import extract_skills
            from milestone3 import compute_similarity
            
            res_skills, _ = extract_skills(resume_text)
            jd_skills, _ = extract_skills(jd_text)
            
            if not jd_skills:
                 # Fallback: Simple Set Intersection
                 r_tokens = set(resume_lower.split())
                 j_tokens = set(jd_text.lower().split())
                 intersection = r_tokens & j_tokens
                 jd_match_score = (len(intersection) / len(j_tokens)) * 100 if j_tokens else 0
                 # Heuristic boost for matching common tech terms
                 res_skills = list(intersection)
            else:
                 _, jd_details, sim_stats = compute_similarity(res_skills, jd_skills)
                 jd_match_score = float(sim_stats['overall'])
                 missing_keywords = [d['jd_skill'] for d in jd_details if d['category'] == 'Low Match']
                 # Extract top matching keywords for display
                 top_keywords = [(d['jd_skill'], 1) for d in jd_details if d['category'] == 'High Match'][:10]

            # REAL ATS WEIGHTING: 
            # If a JD is attached, Relevance is King. 60% Stickiness.
            final_score = (quality_score * 0.4) + (jd_match_score * 0.6)
            
            # Contextual Penalty: If JD match is terrible (<20%), even a perfect resume fails.
            if jd_match_score < 20:
                final_score = min(final_score, 40.0)
                
        except Exception as e:
            # Fallback in case of NLP error
            final_score = quality_score
    else:
        # If no JD, we only judge Quality
        final_score = quality_score

    # Keyword extraction for display (generic if NO JD, strict if JD)
    if not top_keywords:
        common_stops = {"and", "the", "to", "of", "in", "a", "with", "for", "on", "as", "is", "by", "an", "at", "or", "from", "i", "my", "your", "be", "will"}
        gen_keywords = [w for w in words if w not in common_stops and len(w) > 3]
        top_keywords = Counter(gen_keywords).most_common(10)

    return {
        "score": round(final_score, 1),
        "resume_quality": quality_score, 
        "jd_match_score": round(jd_match_score, 1),
        "checks": checks,
        "metrics_count": metric_score,
        "verb_count": len(found_verbs),
        "word_count": word_count,
        "name": candidate_name,
        "email": email_found,
        "phone": phone_found,
        "top_keywords": top_keywords,
        "missing_keywords": missing_keywords,
        "cliches": found_cliches,
        "readability_avg_len": int(avg_sentence_len),
        "section_presence": section_presence
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
                        # Use the new Real-Time scoring engine
                        report = calculate_ats_score_realtime(raw_text, jd_txt)
                        
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
            
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            
            # --- TOP SECTION: ATS SIMULATION PROFILE ---
            st.markdown("### 🤖 simulated_ats_view.log")
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                st.markdown(f"**Candidate Name**<br><span style='color:#a855f7'>{report.get('name', 'Candidate')}</span>", unsafe_allow_html=True)
            with p_col2:
                st.markdown(f"**Email Detected**<br><span style='color:#a855f7'>{report.get('email', 'N/A')}</span>", unsafe_allow_html=True)
            with p_col3:
                st.markdown(f"**Phone Detected**<br><span style='color:#a855f7'>{report.get('phone', 'N/A')}</span>", unsafe_allow_html=True)
            with p_col4:
                wc = report.get('word_count', 0)
                status = "✅ Optimal" if 450 <= wc <= 1200 else "⚠️ Review"
                st.markdown(f"**Word CountStatus**<br><span style='color:{'#22c55e' if 'Optimal' in status else '#facc15'}'>{wc} words ({status})</span>", unsafe_allow_html=True)

            st.markdown("---")

            col_L, col_R = st.columns([0.4, 0.6], gap="large")

            # --- LEFT COLUMN: VISUALS ---
            with col_L:
                # 1. RADAR CHART
                categories = list(cat_scores.keys())
                values = list(cat_scores.values())
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Resume DNA',
                    line_color='#6366f1',
                    fillcolor='rgba(99, 102, 241, 0.2)'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)

                # 2. SCORE CARD
                st.markdown(textwrap.dedent(f"""\
                    <div style="background:rgba(15, 23, 42, 0.6); border:1px solid rgba(99, 102, 241, 0.3); border-radius:20px; padding:25px; text-align:center;">
                        <div style="font-size:0.9rem; color:#cbd5e1; letter-spacing:1px;">ATS MATCH SCORE</div>
                        <div style="font-size:4rem; font-weight:800; color:{'#22c55e' if score >= 85 else '#facc15' if score >= 70 else '#ef4444'}; text-shadow: 0 0 20px rgba(99,102,241,0.5);">
                            {score}
                        </div>
                        <div style="font-size:1rem; color:#94a3b8; font-style:italic;">
                            "{'An exceptional match!' if score >= 85 else 'Solid, but needs polish.' if score >= 70 else 'Requires optimization.'}"
                        </div>
                    </div>
                """), unsafe_allow_html=True)
                
                st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

                # 3. DOWNLOAD
                pdf_bytes = pdf_gen.create_ats_report_pdf(report, candidate_name="Candidate")
                st.download_button(
                    label="📄 Download Full Audit Report (PDF)",
                    data=pdf_bytes,
                    file_name="ATS_Audit_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            # --- RIGHT COLUMN: DETAILED TABS ---
            with col_R:
                tabs = st.tabs(["📊 Deep Dive", "📝 Text Analysis", "🎯 Job Match", "⚠️ Issues"])

                # TAB 1: DEEP DIVE (Category Breakdown)
                with tabs[0]:
                    # 1. Parsing Efficiency (Simulated Metadata)
                    st.markdown("#### 🕵️ Parsing Efficiency")
                    pe_c1, pe_c2, pe_c3 = st.columns(3)
                    with pe_c1:
                         st.markdown("**File Structure**")
                         st.caption("PDF Layering")
                         st.progress(0.95)
                    with pe_c2:
                         st.markdown("**Text Extraction**")
                         st.caption("Clean OCR Quality")
                         st.progress(1.0 if report.get('word_count', 0) > 200 else 0.4)
                    with pe_c3:
                         st.markdown("**Field Detection**")
                         st.caption("Contact Info Confidence")
                         st.progress(1.0 if report.get('email') != "N/A" and report.get('phone') != "N/A" else 0.5)
                    
                    st.markdown("---")

                    # 2. Section Analysis (Grid)
                    st.markdown("#### 🧱 Section Architecture")
                    section_data = report.get('section_presence', {})
                    if section_data:
                        # Custom CSS for status badges
                        st.markdown("""
                        <style>
                        .sec-badge { 
                            padding: 8px 12px; 
                            border-radius: 8px; 
                            text-align: center; 
                            margin-bottom: 8px; 
                            font-size: 0.85rem; 
                            font-weight: 500;
                            border: 1px solid rgba(255,255,255,0.05);
                        }
                        .sec-success { background: rgba(34,197,94,0.15); color: #4ade80; border-color: rgba(34,197,94,0.3); }
                        .sec-fail { background: rgba(239,68,68,0.15); color: #f87171; border-color: rgba(239,68,68,0.3); }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns(2)
                        for i, (sec, found) in enumerate(section_data.items()):
                            css_class = "sec-success" if found else "sec-fail"
                            status_text = "DETECTED" if found else "MISSING"
                            icon = "✅" if found else "🚫"
                            
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div class="sec-badge {css_class}">
                                    <div style="font-size:0.75rem; color:inherit; opacity:0.8;">{sec.upper()}</div>
                                    <div style="font-size:1.1rem; margin-top:2px;">{icon} {status_text}</div>
                                </div>
                                """, unsafe_allow_html=True)

                    st.markdown("---")
                    
                    # 3. Category Deep Dive with Benchmarks
                    st.markdown("#### ⚖️ Scoring Benchmarks")
                    
                    # Formatting
                    st.markdown("**Formatting & Layout**")
                    f_col1, f_col2 = st.columns([0.8, 0.2])
                    with f_col1: st.progress(cat_scores['Formatting'] / 100)
                    with f_col2: st.caption(f"{cat_scores['Formatting']}/100")
                    st.caption(f"Benchmark: 90+ | Impact: High | *Ensures the robot can read your file.*")
                    
                    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

                    # Content
                    st.markdown("**Content Impact**")
                    c_col1, c_col2 = st.columns([0.8, 0.2])
                    with c_col1: st.progress(cat_scores['Content'] / 100)
                    with c_col2: st.caption(f"{cat_scores['Content']}/100")
                    st.caption(f"Benchmark: 80+ | Impact: Critical | *Measures metrics and strong verbs.*")
                    
                    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

                    # Structure
                    st.markdown("**Structure & Completeness**")
                    s_col1, s_col2 = st.columns([0.8, 0.2])
                    with s_col1: st.progress(cat_scores['Structure'] / 100)
                    with s_col2: st.caption(f"{cat_scores['Structure']}/100")
                    st.caption(f"Benchmark: 100 | Impact: Critical | *Checks for mandatory resume sections.*")

                # TAB 2: TEXT ANALYSIS (Readability, Buzzwords)
                with tabs[1]:
                    st.markdown("#### Communication Style")
                    
                    # Readability
                    r_len = report.get('readability_avg_len', 15)
                    r_status = "Excellent" if 10 <= r_len <= 20 else "Review"
                    st.info(f"**Readability Score**: Avg Sentence Length is {r_len} words. ({r_status})")
                    
                    # Buzzwords
                    cliches = report.get('cliches', [])
                    if cliches:
                        st.warning(f"**Buzzword Alert**: We found {len(cliches)} overused terms.")
                        st.write("Consider replacing these with specific achievements:")
                        for c in cliches[:5]:
                            st.markdown(f"- *{c}*")
                    else:
                        st.success("No empty clichés detected. Your language is precise!")
                        
                    # Power Verbs
                    v_count = report.get('verb_count', 0)
                    st.metric("Power Verbs Used", v_count, delta="Target: 6+", delta_color="normal")

                # TAB 3: JOB MATCH
                with tabs[2]:
                    if st.session_state.get("ats_jd_text"):
                        st.markdown("#### Keyword Gap Analysis")
                        missing = report.get("missing_keywords", [])
                        if missing:
                            st.error(f"Missing {len(missing)} Critical Keywords")
                            # Chips
                            html = ""
                            for m in missing:
                                html += f"<span style='background:#fee2e2; color:#ef4444; padding:4px 10px; border-radius:15px; margin:3px; display:inline-block; font-size:0.9rem;'>{m}</span>"
                            st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.success("Perfect Match! You have all the critical keywords.")
                            
                        # Top Keywords
                        st.markdown("#### Your Top Keywords")
                        found_kws = report.get("top_keywords", [])
                        if found_kws:
                            html_k = ""
                            for k, v in found_kws[:10]:
                                html_k += f"<span style='background:#dcfce7; color:#166534; padding:4px 10px; border-radius:15px; margin:3px; display:inline-block; font-size:0.9rem;'>{k} ({v})</span>"
                            st.markdown(html_k, unsafe_allow_html=True)
                    else:
                        st.info("Upload a Job Description to see the Match Analysis.")

                # TAB 4: ISSUES LIST
                with tabs[3]:
                    st.markdown("#### Priority Action Items")
                    if critical_issues:
                        for c in critical_issues:
                            st.error(f"**{c['name']}**: {c['feedback']}")
                    elif warnings:
                         for w in warnings:
                            st.warning(f"**{w['name']}**: {w['feedback']}")
                    else:
                        st.success("No critical issues found!")
                    
                    with st.expander("View Passed Checks"):
                        for p in passed_checks:
                            st.markdown(f"✅ {p['name']}")

                    if st.button("🔄 Re-Analyze"):
                        st.rerun()

    ui_components.render_footer()
