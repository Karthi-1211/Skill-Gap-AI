import streamlit as st
import time
import json
import textwrap
import requests
import random

# -------------------------
# CONFIGURATION
# -------------------------
FEEDBACK_DESTINATION_EMAIL = "balukarthikalamanda@gmail.com" 

def send_feedback_email(data):
    """
    Sends feedback data to email using FormSubmit.co AJAX API.
    """
    url = f"https://formsubmit.co/ajax/{FEEDBACK_DESTINATION_EMAIL}"
    
    payload = data.copy()
    payload["_subject"] = f"feedback from: {data.get('feedback_type', 'General')} from {data.get('name', 'Anonymous')}"
    payload["_template"] = "table"
    payload["_captcha"] = "false"
    
    for k, v in payload.items():
        if isinstance(v, list):
            payload[k] = ", ".join(v)
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": "https://www.streamlit.app/", 
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("success") == "false":
                return False, f"Server Error: {resp_json.get('message', 'Unknown Error')}"
            return True, resp_json
        else:
            if "activate" in response.text.lower():
                return False, f"📧 Activate form at {FEEDBACK_DESTINATION_EMAIL}"
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Connection: {str(e)}"

def app():
    # -------------------------
    # COSMIC OPEN THEME
    # -------------------------
    st.markdown(textwrap.dedent("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&family=Outfit:wght@400;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

            /* 1. DEEP SPACE BACKGROUND */
            .stApp {
                background-color: #030014;
                background-image: 
                    radial-gradient(ellipse at top, #0f172a 0%, #000000 70%),
                    radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.2), transparent 40%),
                    radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.15), transparent 40%);
                background-attachment: fixed;
            }

            /* ANIMATED STARS */
            .stApp::before {
                content: "";
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background-image: 
                    radial-gradient(2px 2px at 50px 200px, #ffffff, rgba(0,0,0,0)),
                    radial-gradient(2px 2px at 200px 30px, #ffffff, rgba(0,0,0,0)),
                    radial-gradient(3px 3px at 50% 50%, #e2e8f0, rgba(0,0,0,0)),
                    radial-gradient(2px 2px at 90% 80%, #ffffff, rgba(0,0,0,0));
                background-size: 300px 300px;
                animation: starMove 120s linear infinite;
                z-index: 0;
                pointer-events: none;
                opacity: 0.6;
            }
            @keyframes starMove { 0% { background-position: 0 0; } 100% { background-position: 300px 300px; } }

            /* 2. LAYOUT & TYPOGRAPHY */
            .block-container { padding-top: 6rem !important; padding-bottom: 5rem !important; max-width: 1150px !important; }
            
            /* Apply Fonts Sparingly to avoid breaking Icons */
            h1, h2, h3, .aurora-font { font-family: 'Outfit', sans-serif !important; }
            p, div, span, input, textarea, button, label { font-family: 'Plus Jakarta Sans', sans-serif !important; }
            
            /* FIX: Ensure Streamlit Icons (Material Symbols) use their own font */
            .st-emotion-cache-1 g > path, .material-icons, .st-emotion-cache-1b0v98t, i, .stIcon {
                font-family: 'Material Icons' !important;
            }

            /* 3. REMOVE BOXES & BORDERS COMPLETELY */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                backdrop-filter: none !important;
            }
            
            /* Target Streamlit Forms - THIS IS THE FIX FOR THE IMAGE ISSUE */
            [data-testid="stForm"] {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }
            
            /* 4. HEADERS (Floating) */
            .box-header {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 30px;
                display:flex; align-items: center; gap: 12px;
                color: #fff;
                text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
            }
            .header-icon {
                font-size: 2rem;
            }
            
            /* 5. INPUTS - Floating on Space */
            .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
                background: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                color: #f8fafc !important;
                border-radius: 12px !important;
                padding: 16px 20px !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
            }
            .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
                background: rgba(255, 255, 255, 0.1) !important;
                border-color: #38bdf8 !important; 
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
            }

            /* 6. NEON BUTTON (ORANGE) - Form Submit Specific */
            div.stButton > button, [data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(90deg, #f97316, #ea580c) !important; /* Orange Gradient */
                border: none !important;
                color: white !important;
                font-weight: 800 !important;
                font-size: 1.2rem !important; 
                border-radius: 20px !important;
                padding: 24px 40px !important;
                transition: all 0.4s ease !important;
                box-shadow: 0 0 20px rgba(249, 115, 22, 0.4) !important;
                width: 100%;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            div.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 0 40px rgba(234, 88, 12, 0.6) !important;
            }

            /* 7. EMOJI DISPLAY (Floating) */
            .rating-display {
                text-align: center;
                margin: 20px 0;
            }
            
            /* 8. TAGS */
            span[data-baseweb="tag"] {
                background: rgba(56, 189, 248, 0.15) !important;
                border: 1px solid rgba(56, 189, 248, 0.3) !important;
                color: #e0f2fe !important;
                border-radius: 20px;
                padding: 4px 10px;
            }
            
            /* 9. EXPANDER FIX */
            div[data-testid="stExpander"] {
                background: rgba(255,255,255,0.03) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                border-radius: 12px !important;
            }
            div[data-testid="stExpander"] summary {
                color: #94a3b8 !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }
            div[data-testid="stExpander"] summary:hover {
                color: white !important;
            }
            /* Correct Icon Font */
            div[data-testid="stExpander"] summary span {
                font-family: 'Material Icons', sans-serif !important; 
            }

            /* 10. PROTECT NAV */
            .floating-nav, .floating-nav *, 
            .custom-sidebar, .custom-sidebar *,
            .full-footer, .full-footer * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                letter-spacing: normal !important;
            }
        </style>
    """), unsafe_allow_html=True)

    # 1. NAVBAR
    import components
    components.render_navbar()

    # 2. HERO HEADER
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<h1 style="font-size: 3.5rem; line-height:1.2; margin-bottom: 10px; color: white;">Help us<br><span style="background: linear-gradient(135deg, #38bdf8 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Reach the Stars</span></h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.1rem; color: #94a3b8; max-width: 450px;">Your feedback is the navigation system for our journey.</p>', unsafe_allow_html=True)
    with c2:
        st.markdown("""
           <div style="height: 160px; display: flex; align-items: center; justify-content: center;">
               <div style="font-size: 6rem; animation: float 6s ease-in-out infinite;">🪐</div>
           </div>
           <style>@keyframes float { 0% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-10px) rotate(5deg); } 100% { transform: translateY(0) rotate(0deg); } }</style>
        """, unsafe_allow_html=True)

    st.write("") 

    # 3. SUCCESS / FORM
    if "feedback_submitted" not in st.session_state:
        st.session_state["feedback_submitted"] = False

    if st.session_state["feedback_submitted"]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=False):
            st.markdown("""
                <div style="text-align: center; padding: 60px 40px; background: rgba(255,255,255,0.03); border-radius: 20px;">
                    <div style="font-size: 5rem; margin-bottom: 20px;">🌠</div>
                    <h2 style="color:white; font-size: 2.2rem; margin-bottom: 10px;">Transmission Complete</h2>
                    <p style="color: #cbd5e1; font-size: 1.2rem;">Data successfully latched to the neural core.</p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,1,1])
            with c2:
                if st.button("Transmit New Signal", use_container_width=True):
                    st.session_state["feedback_submitted"] = False
                    st.rerun()

    else:
        # Layout - BORDERLESS
        st.markdown("<br>", unsafe_allow_html=True)
        col_rank, col_inputs = st.columns([1, 1.8], gap="large")

        with col_rank:
            # NO CONTAINER - Just floating content
            st.markdown('<div class="box-header"><span class="header-icon">✨</span> Your Perspective</div>', unsafe_allow_html=True)
            
            st.markdown("<span style='color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>Overall Satisfaction</span>", unsafe_allow_html=True)
            rating = st.slider("Rating", 1, 10, 8, label_visibility="collapsed")
            
            # Visual Feedback
            emoji_map = {1:"🤬", 2:"😠", 3:"😖", 4:"😕", 5:"😐", 6:"🙂", 7:"😃", 8:"😎", 9:"🤩", 10:"🚀"}
            text_map = {
                1: "Terrible", 2: "Bad", 3: "Poor", 4: "Unsure", 5: "Average", 
                6: "Good", 7: "Very Good", 8: "Excellent", 9: "Amazing", 10: "Mind Blowing"
            }
            
            st.markdown(f"""
                <div class="rating-display">
                    <div style="font-size: 5rem; filter: drop-shadow(0 0 30px rgba(56, 189, 248, 0.4)); animation: float 4s ease-in-out infinite;">
                        {emoji_map.get(rating, "😐")}
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #fff; margin-top: 20px; letter-spacing: 1px;">
                        {text_map.get(rating, "Average")}
                    </div>
                    <div style="height: 2px; width: 50px; background: #38bdf8; margin: 15px auto; opacity: 0.5;"></div>
                </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.markdown("<span style='color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>Highlights</span>", unsafe_allow_html=True)
            st.multiselect(
                "Select tags",
                ["Visual Perfection", "Blazing Speed", "Smart AI", "Easy Navigation", "Mobile Friendly"],
                label_visibility="collapsed"
            )

        with col_inputs:
            st.markdown('<div class="box-header"><span class="header-icon">📨</span> Share Details</div>', unsafe_allow_html=True)

            with st.form("space_form"):
                
                # 1. CATEGORY
                st.write("**Category**")
                f_type = st.radio(
                    "Category",
                    ["General Feedback", "Feature Request", "Bug Report", "Collaboration"],
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                
                # 2. PRIORITY / CONTEXT FEATURES
                if f_type == "Bug Report":
                    st.write("**Bug Details**")
                    c_bug1, c_bug2 = st.columns(2)
                    with c_bug1:
                        st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], label_visibility="collapsed")
                    with c_bug2:
                        st.selectbox("Frequency", ["Once", "Intermittent", "Consistent"], label_visibility="collapsed")
                elif f_type == "Feature Request":
                    st.write("**Impact Level**")
                    st.select_slider("How important is this?", options=["Nice-to-have", "Important", "Game Changer"], label_visibility="collapsed")

                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                
                # 3. CONTACT INFO
                cols = st.columns(2)
                with cols[0]:
                    st.write("**Name**")
                    name = st.text_input("Name", placeholder="Your Name", label_visibility="collapsed")
                with cols[1]:
                    st.write("**Email**")
                    email = st.text_input("Email", placeholder="name@example.com", label_visibility="collapsed")

                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                
                # 4. MESSAGE
                st.write("**Message**")
                msg = st.text_area("Message", height=120, placeholder="Tell us more...", label_visibility="collapsed")
    
                
                # 6. CONTACT PREF
                st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
                contact_ok = st.checkbox("It's okay to contact me about this feedback", value=True)

                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Launch Feedback")
                
                if submit:
                    if not name.strip() or not email.strip() or not msg.strip():
                        st.error("🚨 Missing Info: Please enter your Name, Email, and Message.")
                    elif "@" not in email or "." not in email:
                        st.error("🚨 Invalid Email: Please enter a valid email address.")
                    else:
                        with st.spinner("Uploading to Orbit..."):
                            time.sleep(1)
                            data = {
                                "name": name,
                                "email": email,
                                "feedback_type": f_type,
                                "message": msg,
                                "rating": rating,
                                "contact_consent": contact_ok
                            }
                            success, resp = send_feedback_email(data)
                            if success:
                                st.session_state["feedback_submitted"] = True
                                st.rerun()
                            else:
                                st.error(f"Error: {resp}")

    # FOOTER
    components.render_footer()

if __name__ == "__main__":
    st.set_page_config(page_title="Feedback", layout="wide")
    app()
