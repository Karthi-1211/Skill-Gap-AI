import streamlit as st
import base64
import os
import time
import requests
import json
import uuid
from streamlit.components.v1 import html

# -------------------------------------------------------
# DATA PERSISTENCE
# -------------------------------------------------------
SESSION_FILE = "user_session.json"

EXCLUDED_PREFIXES = (
    "btn_", "dash_btn_", "d_card_", "nav_toggle", "updater_", 
    "dd_", "adv_", "int_", "prep_btn_", "gap_check_",
    "nav_btn_", "home_tool_btn_", "home_dash_btn_", "continue_btn_", "launch_", "dash_reset_", "dash_acc_",
    "ai_", "sv_", "del_",
    "j_up", "r_up", "ats_resume_uploader", "uploader_"
)

def reset_student_session():
    """Clears ephemeral student data for a fresh start."""
    persist_exact = {
        "jobs", "applications", "selected_candidate_id", "selected_app_id", "hr_active_tab_index"
    }
    
    # Identify keys to delete (everything NOT persistent)
    keys_to_del = []
    for k in st.session_state.keys():
        if k in persist_exact or k.startswith("hr_"):
            continue
        keys_to_del.append(k)
        
    for k in keys_to_del:
        del st.session_state[k]
        
    # Generate new session ID to be safe
    st.session_state["session_uid"] = str(uuid.uuid4())[:8]
    
    # Clear URL params to prevent reloading old session
    st.query_params.clear()
    
    # Reset Navigation to Milestone 1
    st.session_state["nav_page"] = "Milestone 1: Data Ingestion"
    
    st.rerun()

def save_progress():
    """Saves the current session state to a local JSON file ONLY if data changed."""
    import hashlib
    try:
        # Filter serializable data & exclude UI-only buttons/widgets
        data = {k: v for k, v in st.session_state.items() 
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
                and not k.startswith(EXCLUDED_PREFIXES)
                and k != "nav_page" and k != "_last_save_hash"}
        
        # Optimize: Check hash before writing
        json_str = json.dumps(data)
        current_hash = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        
        if st.session_state.get("_last_save_hash") == current_hash:
            return 
            
        with open(SESSION_FILE, "w") as f:
            f.write(json_str)
            
        st.session_state["_last_save_hash"] = current_hash
            
    except Exception as e:
        pass

def load_progress():
    """Loads session state from the local JSON file with Session Token logic."""
    if "session_uid" not in st.session_state:
        st.session_state["session_uid"] = str(uuid.uuid4())[:8]

    # -------------------------------------------------------------
    # OPTIMIZATION: SKIP DISK READ IF DATA IS WARM
    # -------------------------------------------------------------
    
    has_data = "jobs" in st.session_state and "applications" in st.session_state
    
    params = st.query_params
    url_uid = params.get("uid", None) 
    current_uid = st.session_state.get("session_uid")
    
    # If URL uid matches current, or is missing, AND we have data -> Skip Load
    if has_data:
        # P.S. params values can be list or string depending on streamlit version/usage, handle carefully
        if not url_uid:
            return
        
        val = url_uid[0] if isinstance(url_uid, list) else url_uid
        if str(val) == str(current_uid):
             return

    # -------------------------------------------------------------
    # SLOW PATH: DISK LOAD
    # -------------------------------------------------------------
    if not os.path.exists(SESSION_FILE):
        return

    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            
        # 1. Get UID from Saved Data
        saved_uid = data.get("session_uid", "no_match")
        
        # 2. Determine Mode
        is_navigation = True 
        if url_uid and saved_uid:
             u_val = url_uid[0] if isinstance(url_uid, list) else url_uid
             if str(u_val) != str(saved_uid):
                 is_navigation = False
        elif not url_uid:
             #Fresh Load without uid in URL
             is_navigation = False

        persist_exact = {
            "jobs", "applications", "selected_candidate_id", "selected_app_id", "hr_active_tab_index"
        }

        for k, v in data.items():
            if k == "nav_page": continue
            
            # Safety check: Do not load keys that are in the exclusion list
            if k.startswith(EXCLUDED_PREFIXES):
                continue
            
            should_load = False
            if is_navigation:
                should_load = True
            else:
                if k in persist_exact or k.startswith("hr_"):
                    should_load = True
            
            if should_load:
                 if k not in st.session_state:
                    st.session_state[k] = v
        
        # 3. Sync Session ID
        if is_navigation and saved_uid != "no_match":
            st.session_state["session_uid"] = saved_uid

    except Exception as e:
        pass

# -------------------------------------------------------
# NAVIGATION LOGIC
# -------------------------------------------------------
PAGE_MAP = {
    "home": "Home",
    "m1": "Milestone 1: Data Ingestion",
    "m2": "Milestone 2: Skill Extraction",
    "m3": "Milestone 3: Gap Analysis",
    "m4": "Milestone 4: Dashboard & Report",

    "ats": "ATS Report",

    "feedback": "Feedback",
    "contact": "Contact Us",
    "hr": "HR Dashboard",
    "student_dashboard": "Student Dashboard",
    "resume_builder": "Resume Builder"
}

def navigate_to(page_name):
    """
    Callback function to handle navigation.
    Updates session state and query parameters.
    """
    st.session_state["nav_page"] = page_name
    reverse_map = {v: k for k, v in PAGE_MAP.items()}
    if page_name in reverse_map:
        st.query_params["page"] = reverse_map[page_name]

# -------------------------------------------------------
# LOTTIE ANIMATIONS
# -------------------------------------------------------
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

@st.cache_data
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# -------------------------------------------------------
# UI COMPONENTS
# -------------------------------------------------------

def get_image_base64(path):
    try:
        if not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_logo_svg():
    return '<svg width="35" height="35" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon"><defs><linearGradient id="grad4" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#22D3EE" /><stop offset="100%" stop-color="#3B82F6" /></linearGradient><filter id="glow4" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><rect x="10" y="10" width="44" height="44" rx="12" stroke="url(#grad4)" stroke-width="4" fill="none"/><path d="M24 36L30 36L28 46L40 28L34 28L36 18L24 36Z" fill="white" filter="url(#glow4)"/><circle cx="32" cy="8" r="3" fill="#22D3EE"/><circle cx="32" cy="56" r="3" fill="#3B82F6"/><circle cx="8" cy="32" r="3" fill="#22D3EE"/><circle cx="56" cy="32" r="3" fill="#3B82F6"/></svg>'

def apply_theme():
    """Injects global CSS variables and styles for the Dark theme."""
    colors = {
        "BODY_BG": "linear-gradient(180deg, #0f172a 0%, #071032 35%, #041126 100%)",
        "SIDEBAR_BG": "#0f172a",
        "TEXT_COLOR": "#e6eef8",
        "CARD_BG": "rgba(30, 41, 59, 0.7)",
        "CARD_BORDER": "1px solid rgba(148, 163, 184, 0.1)",
        "MUTED": "#9fb0d4",
        "ACCENT": "#3b82f6",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "ERROR": "#ef4444",
        "SHADOW": "0 10px 30px rgba(0,0,0,0.5)",
        "NAV_BG": "rgba(15, 23, 42, 0.8)"
    }
    
    css = f"""
    <style>
    :root {{
        --body-bg: {colors['BODY_BG']};
        --sidebar-bg: {colors['SIDEBAR_BG']};
        --text-color: {colors['TEXT_COLOR']};
        --card-bg: {colors['CARD_BG']};
        --card-border: {colors['CARD_BORDER']};
        --muted-color: {colors['MUTED']};
        --accent-color: {colors['ACCENT']};
        --success-color: {colors['SUCCESS']};
        --warning-color: {colors['WARNING']};
        --error-color: {colors['ERROR']};
        --card-shadow: {colors['SHADOW']};
        --nav-bg: {colors['NAV_BG']};
    }}

    /* Global App Background */
    .stApp {{
        background: {colors['BODY_BG']} !important;
        color: {colors['TEXT_COLOR']} !important;
    }}
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, li, span, div {{
        color: {colors['TEXT_COLOR']};
    }}
    
    /* Muted Text */
    .muted {{
        color: {colors['MUTED']} !important;
    }}

    /* Cards (Generic) */
    .stCard, .css-1r6slb0, .css-12w0qpk {{
        background-color: {colors['CARD_BG']};
        border: {colors['CARD_BORDER']};
        border-radius: 12px;
        padding: 20px;
        box-shadow: {colors['SHADOW']};
    }}

    /* Input Fields */
    .stTextArea textarea, .stTextInput input {{
        background-color: {colors['CARD_BG']} !important;
        color: {colors['TEXT_COLOR']} !important;
        border: 1px solid {colors['ACCENT']}40 !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background: linear-gradient(135deg, {colors['ACCENT']}, {colors['ACCENT']}dd) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }}
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px {colors['ACCENT']}66;
    }}

    /* Custom Nav Styling */
    .custom-nav {{
        background-color: {colors['NAV_BG']};
        padding: 20px;
        border-radius: 12px;
        border: {colors['CARD_BORDER']};
        box-shadow: {colors['SHADOW']};
        height: 100%;
    }}
    
    /* Radio Button Styling in Nav */
    .stRadio label {{
        color: {colors['TEXT_COLOR']} !important;
        font-weight: 500;
        padding: 8px;
        border-radius: 6px;
        transition: background 0.2s;
    }}
    .stRadio label:hover {{
        background-color: {colors['ACCENT']}15;
    }}

    [data-testid="stSpinner"] {{
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 999999 !important;
        
        /* Glassmorphism Card Style */
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
        
        /* Sizing & Layout */
        width: auto !important;
        min-width: 280px !important; 
        padding: 40px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 20px !important;
    }}

    /* Style the text inside spinner */
    [data-testid="stSpinner"] p {{
        color: #e2e8f0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        font-family: 'Inter', sans-serif !important;
        margin: 0 !important;
    }}
    
    /* Target the spinner SVG itself if possible, standardizing size */
    [data-testid="stSpinner"] > div {{
        margin-bottom: 10px !important;
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return colors

def render_navbar():
    logo_svg = get_logo_svg()

    curr_uid = st.session_state.get("session_uid", "")
    session_query = f"&uid={curr_uid}" if curr_uid else ""

    navbar_css = f"""
    <style>
    html {{
        scroll-behavior: auto !important;
    }}
    .floating-nav {{
        position: fixed !important;
        top: 60px !important;
        left: 0 !important;
        width: 100% !important;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        height: 70px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30px;
        z-index: 999999 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin: 0 !important;
    }}
    .nav-left {{ display: flex; align-items: center; gap: 20px; }}
    .nav-logo {{ 
        font-weight: 800; font-size: 1.2rem; color: white; letter-spacing: 1px; 
        display: flex; align-items: center; gap: 10px; 
    }}
    .nav-links {{ display: flex; gap: 20px; align-items: center; }}
    .nav-item {{ 
        color: #e2e8f0 !important; 
        text-decoration: none !important; 
        font-size: 0.9rem; 
        font-weight: 600; 
        cursor: pointer; 
        transition: all 0.3s ease;
        padding: 8px 20px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        display: inline-block;
    }}
    .nav-item:hover {{ 
        background: #3b82f6 !important; 
        color: white !important; 
        border-color: #3b82f6 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        text-decoration: none !important;
    }}
    .nav-item:visited {{ color: #e2e8f0 !important; text-decoration: none !important; }}
    .nav-item:active {{ transform: translateY(0); text-decoration: none !important; }}

    #nav-toggle {{ display: none; }}

    .hamburger-label {{
        color: white; font-size: 1.5rem; cursor: pointer;
        padding: 5px; transition: transform 0.2s;
        user-select: none;
    }}
    .hamburger-label:hover {{ transform: scale(1.1); color: #3b82f6; }}

    .custom-sidebar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 340px;
        height: 100vh;
        background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
        z-index: 1000000;
        transform: translateX(-110%);
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 20px 0 50px rgba(0,0,0,0.6);
        display: flex;
        flex-direction: column;
        border-right: 1px solid rgba(255,255,255,0.05);
    }}

    #nav-toggle:checked ~ .custom-sidebar {{
        transform: translateX(0);
    }}

    .sidebar-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.6);
        z-index: 999998;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        backdrop-filter: blur(4px);
    }}

    #nav-toggle:checked ~ .sidebar-overlay {{
        opacity: 1;
        pointer-events: auto;
    }}

    .sidebar-header {{
        padding: 30px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.01);
    }}
    .close-btn {{
        background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer;
        transition: color 0.2s;
    }}
    .close-btn:hover {{ color: white; transform: rotate(90deg); }}

    .sidebar-profile {{
        padding: 25px;
        background: rgba(255,255,255,0.02);
        display: flex; align-items: center; gap: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    .profile-pic {{
        width: 54px; height: 54px; border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 1.2rem; color: white;
        border: 2px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}

    .sidebar-menu {{
        padding: 20px;
        flex-grow: 1;
        overflow-y: auto;
    }}
    .menu-category {{
        font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700;
        margin-bottom: 12px; margin-top: 24px; letter-spacing: 1.2px;
        padding-left: 5px;
    }}
    .menu-item {{
        display: flex; align-items: center; gap: 14px;
        padding: 14px 18px;
        color: #cbd5e1 !important;
        text-decoration: none !important;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}
    .menu-item:hover {{
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05)) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        color: white !important;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .menu-item:active {{ transform: scale(0.98); }}
    .menu-icon {{ width: 24px; text-align: center; font-size: 1.1rem; }}

    .upgrade-card {{
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 0 20px 20px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    .upgrade-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
    }}
    .upgrade-btn {{
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 12px;
        cursor: pointer;
        width: 100%;
        transition: opacity 0.2s;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }}
    .upgrade-btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}

    .sidebar-footer {{
        padding: 20px;
        border-top: 1px solid rgba(255,255,255,0.05);
        font-size: 0.8rem; color: #64748b; text-align: center;
        background: rgba(0,0,0,0.2);
    }}
    </style>
    """

    navbar_html = f"""
<input type="checkbox" id="nav-toggle">
<!-- Overlay -->
<div class="sidebar-overlay">
<label for="nav-toggle" style="width:100%;height:100%;display:block;cursor:default;"></label>
</div>
<!-- Sidebar -->
<div class="custom-sidebar">
<div class="sidebar-header">
<div style="font-weight:800; font-size:1.2rem; color:white; display:flex; align-items:center; gap:10px;">
{logo_svg} SkillGapAI
</div>
<label for="nav-toggle" class="close-btn">&times;</label>
</div>
<div class="sidebar-profile">
<div class="profile-pic">BK</div>
<div>
<div style="color:white; font-weight:600;">Balu Karthik</div>
<div style="color:#94a3b8; font-size:0.8rem;">Free Plan</div>
</div>
</div>
<div class="sidebar-menu">
<div class="menu-category">Start</div>
<a href="/?page=home{session_query}" class="menu-item" target="_self">
<span class="menu-icon">🏠</span> Home
</a>

<div class="menu-category">Milestone Workflow</div>
<a href="/?page=m1{session_query}" class="menu-item" target="_self">
<span class="menu-icon">📂</span> 1. Data Ingestion
</a>
<a href="/?page=m2{session_query}" class="menu-item" target="_self">
<span class="menu-icon">🧠</span> 2. Skill Extraction
</a>
<a href="/?page=m3{session_query}" class="menu-item" target="_self">
<span class="menu-icon">📊</span> 3. Gap Analysis
</a>
<a href="/?page=m4{session_query}" class="menu-item" target="_self">
<span class="menu-icon">📈</span> 4. Report & Dashboard
</a>

<div class="menu-category">Career Tools</div>
<a href="/?page=ats{session_query}" class="menu-item" target="_self">
<span class="menu-icon">✅</span> ATS Checker
</a>
<a href="/?page=resume_builder{session_query}" class="menu-item" target="_self">
<span class="menu-icon">📝</span> Resume Builder
</a>

<div class="menu-category">Dashboards</div>
<a href="/?page=student_dashboard{session_query}" class="menu-item" target="_self">
<span class="menu-icon">🎓</span> Student Dashboard
</a>
<a href="/?page=hr{session_query}" class="menu-item" target="_self">
<span class="menu-icon">👥</span> Recruiter Portal
</a>

<div class="menu-category">Support</div>
<a href="/?page=feedback{session_query}" class="menu-item" target="_self">
<span class="menu-icon">💬</span> Feedback
</a>
<a href="/?page=contact{session_query}" class="menu-item" target="_self">
<span class="menu-icon">📞</span> Contact Us
</a>

<div class="menu-category">System Status</div>
<div class="menu-item" style="cursor:default; opacity:0.9;">
<span class="menu-icon">🟢</span> All Systems Normal
</div>
<div class="menu-item" style="cursor:default; opacity:0.9;">
<span class="menu-icon">🔋</span> v1.2.0 (Stable)
</div>
</div>

<div class="sidebar-footer">
&copy; 2025 SkillGapAI Inc.<br>v1.2.0
</div>
</div>
<!-- Navbar -->
<div class="floating-nav">
<div class="nav-left">
<label for="nav-toggle" class="hamburger-label">☰</label>
<div class="nav-logo">{logo_svg}<span style="margin-left:10px;">SkillGapAI</span></div>
</div>
<div class="nav-links">
<a href="/?page=home{session_query}" target="_self" class="nav-item">Home</a>
<a href="/?page=feedback{session_query}" target="_self" class="nav-item">Feedback</a>
<a href="/?page=contact{session_query}" target="_self" class="nav-item">Contact</a>
</div>
</div>
"""
    st.markdown(navbar_css, unsafe_allow_html=True)
    st.markdown(navbar_html, unsafe_allow_html=True)

def scroll_to_top(smooth: bool = False, delay_ms: int = 50, key: str = None, **html_kwargs):
    import streamlit.components.v1 as scomponents

    behavior = "smooth" if smooth else "auto"
    # multiple attempts (immediate, rAF, short timeouts) to ensure we run after layout finishes
    js = (
        "<script>"
        "(function(){"
        f"  const behavior = '{behavior}';"
        "  function st0(){"
        "    try{ window.parent.scrollTo({top:0,left:0,behavior}); }catch(e){ window.parent.scrollTo(0,0); }"
        "  }"
        "  st0();"
        "  requestAnimationFrame(st0);"
        "  setTimeout(st0, 50);"
        "  setTimeout(st0, 150);"
        "})();"
        "</script>"
    )

    html_kwargs.pop("key", None)
    html_kwargs.setdefault("height", 1)
    scomponents.html(js, **html_kwargs)

def render_stepper(current_step: int = 1):
    steps = ["Ingestion", "Extraction", "Analysis", "Report"]

    html = '<div style="display:flex; justify-content:space-between; margin-bottom:30px; padding:0 20px; position:relative;">'

    for i, step in enumerate(steps, 1):
        color = "#3B82F6" if i <= current_step else "#E5E7EB"
        text_color = "#1E293B" if i <= current_step else "#9CA3AF"
        weight = "700" if i == current_step else "500"

        html += (
            "<div style=\"display:flex; align-items:center; flex-direction:column; "
            "position:relative; z-index:1;\">"
        )
        html += (
            f'<div style="width:30px; height:30px; border-radius:50%; '
            f'background:{color}; color:white; display:flex; align-items:center; '
            f'justify-content:center; font-weight:bold; font-size:14px; '
            f'box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">{i}</div>'
        )
        html += (
            f'<div style="margin-top:8px; font-size:12px; color:{text_color}; '
            f'font-weight:{weight};">{step}</div>'
        )
        html += "</div>"

    html += '<div style="position:absolute; top:15px; left:50px; right:50px; height:2px; background:#E5E7EB; z-index:0;"></div>'

    if current_step > 1:
        width_pct = min(100, (current_step - 1) * 33)
        html += (
            f'<div style="position:absolute; top:15px; left:50px; width:{width_pct}%; '
            f'height:2px; background:#3B82F6; z-index:0;"></div>'
        )

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_footer():
    footer = """
    <style>
    [data-testid="stAppViewContainer"],
    [data-testid="stDecoration"],
    .main > div {
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    [data-testid="stAppViewContainer"] {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        overflow-x: hidden;
    }
    
    [data-testid="stMain"] {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-x: hidden;
    }
    
    [data-testid="block-container"] {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding-bottom: 0 !important;
        max-width: 100vw !important;
        overflow-x: hidden;
    }
    
    /* Push the footer wrapper to the bottom */
    [data-testid="stVerticalBlock"] > div:has(.full-footer) {
        margin-top: auto;
        width: 100vw;
    }

    .full-footer {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        margin-top: 200px; /* Gap between content and footer */
        /* Aggressive hack to cover bottom gap */
        margin-bottom: -200px;
        padding-bottom: 20px;
        
        background: linear-gradient(to bottom, #0f172a, #020617);
        color: #94a3b8;
        padding-top: 40px;
        padding-left: 20px;
        padding-right: 20px;
        border-top: 1px solid rgba(255,255,255,0.05);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
        z-index: 9999;
    }
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1.5fr 0.8fr 0.8fr 0.8fr 1fr;
        gap: 15px;
        padding: 0 20px;
    }

    .footer-brand h2 {
        color: white;
        font-size: 1.4rem;
        margin-bottom: 10px;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .footer-brand p {
        line-height: 1.5;
        opacity: 0.9;
        max-width: 360px;
        margin-bottom: 15px;
        font-size: 0.85rem;
    }

    .social-links {
        display: flex;
        gap: 10px;
    }

    .social-icon {
        width: 32px;
        height: 32px;
        background: rgba(255,255,255,0.08);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
        text-decoration: none !important;
    }

    .social-icon:hover {
        background: #3b82f6;
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(59,130,246,0.4);
    }

    .footer-links h3 {
        color: white;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 0.95rem;
    }

    .footer-links a {
        color: #94a3b8;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
        transition: all 0.2s;
        font-size: 0.8rem;
    }

    .footer-links a:hover {
        color: #60a5fa;
        transform: translateX(4px);
    }

    .contact-item {
        display: flex;
        gap: 10px;
        align-items: flex-start;
        margin-bottom: 8px;
        font-size: 0.8rem;
    }

    .contact-icon {
        color: #3b82f6;
        font-size: 0.9rem;
        margin-top: 2px;
    }

    .footer-bottom {
        max-width: 1200px;
        margin: 20px auto 0;
        padding: 10px 20px 0;
        border-top: 1px solid rgba(255,255,255,0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #64748b;
        font-size: 0.75rem;
    }

    .footer-bottom-links a {
        color: #64748b;
        text-decoration: none;
        margin-left: 20px;
    }

    .footer-bottom-links a:hover { color: #94a3b8; }

    @media (max-width: 1024px) {
        .footer-content { grid-template-columns: 1fr 1fr 1fr; }
        .footer-brand { grid-column: 1 / -1; text-align: center; }
        .footer-brand p { margin: 0 auto 15px; }
        .social-links { justify-content: center; }
    }

    @media (max-width: 640px) {
        .footer-content { grid-template-columns: 1fr; text-align: center; }
        .contact-item { justify-content: center; }
        .footer-bottom { flex-direction: column; gap: 10px; }
        .footer-bottom-links a { margin: 0 8px; }
    }
    </style>

    <div class="full-footer">
        <div class="footer-content">
            <div class="footer-brand">
                <h2>SkillGapAI</h2>
                <p>Bridging the gap between talent and opportunity. We use advanced AI to analyze your skills, optimize your resume, and guide your career path with precision.</p>
                <div class="social-links">
                    <a href="#" class="social-icon">🐦</a>
                    <a href="#" class="social-icon">🔗</a>
                    <a href="#" class="social-icon">📸</a>
                    <a href="#" class="social-icon">📺</a>
                </div>
            </div>
            <!-- Your 4 columns exactly as before -->
            <div class="footer-links">
                <h3>Platform</h3>
                <a href="#">Home</a><a href="#">Skill Analysis</a><a href="#">Resume Optimizer</a><a href="#">Learning Paths</a><a href="#">Success Stories</a>
            </div>
            <div class="footer-links">
                <h3>Company</h3>
                <a href="#">About Us</a><a href="#">Careers</a><a href="#">Blog</a><a href="#">Press Kit</a><a href="#">Partners</a>
            </div>
            <div class="footer-links">
                <h3>Resources</h3>
                <a href="#">Help Center</a><a href="#">API Documentation</a><a href="#">Community Hub</a><a href="#">Developer Blog</a><a href="#">AI Ethics</a>
            </div>
            <div class="footer-links">
                <h3>Contact Us</h3>
                <div class="contact-item"><div class="contact-icon">Email</div><div>support@skillgap.ai</div></div>
                <div class="contact-item"><div class="contact-icon">Phone</div><div>+91 1111111111</div></div>
                <div class="contact-item"><div class="contact-icon">Location</div><div>123 Innovation<br>Tech City, Visakhapatnam</div></div>
            </div>
        </div>
        <div class="footer-bottom">
            <div>© 2025 SkillGapAI Inc. All rights reserved.</div>
            <div class="footer-bottom-links">
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Cookie Settings</a>
            </div>
        </div>
    </div>
    """
    
    st.markdown(footer, unsafe_allow_html=True)

def get_page_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    :root {
        --card-bg: #020617;
        --card-border: 1px solid #1f2937;
        --card-shadow: 0 10px 40px rgba(15,23,42,0.6);
        --text-color: #e5e7eb;
        --muted-color: #9ca3af;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --error-color: #ef4444;
        --warning-color: #f59e0b;
        --footer-height: 72px;
    }

    /* Global Background Enhancement */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 60%) !important;
        background-attachment: fixed !important;
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out forwards;
        opacity: 0; /* Start hidden */
    }
    
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Footer Fix */
    .block-container { 
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    /* Ensure no extra spacing from Streamlit */
    footer { display: none !important; }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 60%) !important;
        background-attachment: fixed !important;
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(120deg, #2563EB, #1E40AF);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
        margin-top: 20px;
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px; display: flex; align-items: center; justify-content: center; gap: 15px; }
    .hero-sub { font-size: 1.1rem; opacity: 0.9; font-weight: 300; }
    
    /* Logo Animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    .logo-icon {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Card Styling - PREMIUM BOXES */
    .m3-card, .metric-box, .metric-card, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 20px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    
    .m3-card:hover, .metric-box:hover, .metric-card:hover, div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1) !important;
        border-color: rgba(108, 60, 240, 0.5) !important;
    }

    /* Metric Values */
    .metric-val, .m3-metric-val {
        font-size: 2rem;
        font-weight: 800;
        color: var(--accent-color);
    }
    .metric-lbl, .m3-metric-label {
        font-size: 0.85rem;
        color: var(--muted-color);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        background: #020617;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border-bottom: 2px solid var(--accent-color);
    }
    </style>
    """