import streamlit as st

import time
import json
import os
import textwrap
# For deployment, prefer storing this in st.secrets
CONTACT_DESTINATION_EMAIL = "balukarthikalamanda@gmail.com"

def send_contact_email(data):
    """
    Sends contact form data to email using FormSubmit.co AJAX API.
    """
    import requests
    # Use the AJAX endpoint to get a JSON response
    url = f"https://formsubmit.co/ajax/{CONTACT_DESTINATION_EMAIL}"
    
    payload = data.copy()
    payload["_subject"] = f"SkillGap AI Contact: {data.get('subject', 'New Message')} from {data.get('name', 'Anonymous')}"
    payload["_template"] = "table"  
    payload["_captcha"] = "false"

    for k, v in payload.items():
        if isinstance(v, list):
            payload[k] = ", ".join(v)
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": "https://www.streamlit.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Timeout set to 60s to allow for slow server response / activation triggers
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("success") == "false":
                return False, f"Server Error: {resp_json.get('message', 'Unknown Error')}"
            return True, resp_json
        else:
            if "activate" in response.text.lower():
                return False, "📧 Action Required: Check your email to Activate this form."
            return False, f"Status: {response.status_code}, Body: {response.text}"
    except Exception as e:
        print(f"DEBUG: FormSubmit Error: {e}")
        return False, f"Connection Error: {str(e)}"

def app():
    # -------------------------
    # CUSTOM CSS FOR HOLOGRAPHIC THEME
    # -------------------------
    st.markdown(textwrap.dedent("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

            /* GLOBAL WRAPPER & ANIMATED BG */
            .stApp {
                background-color: #020617;
                background-image: 
                    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%), 
                    radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.1) 0px, transparent 50%),
                    linear-gradient(rgba(2, 6, 23, 1), rgba(2, 6, 23, 1));
            }
            
            /* GRID OVERLAY */
            .stApp::before {
                content: "";
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background-image: 
                    linear-gradient(rgba(6, 182, 212, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(6, 182, 212, 0.05) 1px, transparent 1px);
                background-size: 50px 50px;
                pointer-events: none;
                z-index: 0;
            }

            /* REMOVE PADDING */
            .block-container { padding-bottom: 0 !important; max-width: 1200px !important; }

            /* HOLOGRAM TITLE */
            .holo-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 4rem;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 4px;
                color: transparent;
                -webkit-text-stroke: 1px rgba(6, 182, 212, 0.8);
                text-shadow: 0 0 30px rgba(6, 182, 212, 0.5);
                position: relative;
                margin-top: 50px;
                margin-bottom: 10px;
                animation: glitch-text 3s infinite alternate-reverse;
            }
            .holo-title::before {
                content: "CONTACT NODE";
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                color: rgba(6, 182, 212, 0.5);
                -webkit-text-stroke: 0;
                filter: blur(4px);
                z-index: -1;
            }
            
            .holo-subtitle {
                text-align: center;
                font-family: 'Rajdhani', sans-serif;
                color: #94a3b8;
                font-size: 1.2rem;
                letter-spacing: 1px;
                margin-bottom: 60px;
                text-shadow: 0 0 10px rgba(148, 163, 184, 0.3);
            }

            /* INFO CARDS - CYBER STYLE */
            .info-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-bottom: 50px;
            }
            .holo-card {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(6, 182, 212, 0.2);
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }
            .holo-card:hover {
                background: rgba(6, 182, 212, 0.05);
                border-color: rgba(6, 182, 212, 0.6);
                box-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
                transform: translateY(-5px);
            }
            .holo-card::after {
                content: '';
                position: absolute;
                top: 0; left: -100%; width: 50%; height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transform: skewX(-25deg);
                transition: 0.5s;
            }
            .holo-card:hover::after { left: 150%; }
            
            .holo-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
                filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.8));
                animation: float 4s ease-in-out infinite;
            }
            .holo-card h3 {
                color: #e2e8f0;
                font-family: 'Orbitron', sans-serif;
                font-size: 1.2rem;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
            .holo-card p {
                color: #94a3b8;
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.1rem;
                margin: 0;
            }

            /* MAIN FORM CONTAINER - ENHANCED */
            [data-testid="stForm"] {
                background: rgba(2, 6, 23, 0.7);
                border: 1px solid rgba(168, 85, 247, 0.3);
                border-radius: 20px;
                padding: 10px; 
                position: relative;
                box-shadow: 0 0 50px rgba(168, 85, 247, 0.1), inset 0 0 20px rgba(168, 85, 247, 0.05);
                overflow: visible;
                backdrop-filter: blur(10px);
                margin-top: 20px;
            }


            /* Glowing corners - PULSING */
            .corner-accent {
                position: absolute;
                width: 30px; height: 30px;
                border: 2px solid #a855f7;
                transition: all 0.3s ease;
                z-index: 20;
                box-shadow: 0 0 10px rgba(168, 85, 247, 0.6);
            }
            .tl { top: -2px; left: -2px; border-right: none; border-bottom: none; border-radius: 15px 0 0 0; animation: pulse-corner 2s infinite; }
            .tr { top: -2px; right: -2px; border-left: none; border-bottom: none; border-radius: 0 15px 0 0; animation: pulse-corner 2s infinite 0.5s; }
            .bl { bottom: -2px; left: -2px; border-right: none; border-top: none; border-radius: 0 0 0 15px; animation: pulse-corner 2s infinite 1s; }
            .br { bottom: -2px; right: -2px; border-left: none; border-top: none; border-radius: 0 0 15px 0; animation: pulse-corner 2s infinite 1.5s; }
            
            @keyframes pulse-corner {
                0%, 100% { box-shadow: 0 0 5px rgba(168, 85, 247, 0.6); border-color: #a855f7; }
                50% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.8); border-color: #06b6d4; }
            }
            
            [data-testid="stForm"]:hover .corner-accent {
                width: 50px; height: 50px;
                box-shadow: 0 0 25px #a855f7;
            }

            /* FORM HEADER - TERMINAL STYLE */
            .cyber-header {
                font-family: 'Orbitron', monospace;
                color: #e2e8f0;
                font-size: 1.5rem;
                border-bottom: 1px solid rgba(168, 85, 247, 0.3);
                padding-bottom: 15px;
                margin-bottom: 25px;
                display: block;
                position: relative;
            }
            .cyber-header::after {
                content: '_';
                animation: blink 1s infinite;
                color: #06b6d4;
            }
            @keyframes blink { 50% { opacity: 0; } }

            /* INPUT STYLING OVERRIDES */
            .stTextInput > div > div > input, .stTextArea > div > div > textarea {
                background: rgba(15, 23, 42, 0.6) !important;
                border: 1px solid rgba(148, 163, 184, 0.2) !important;
                color: #f8fafc !important;
                font-family: 'Rajdhani', sans-serif !important;
                font-size: 1.1rem !important;
                border-radius: 4px !important;
                transition: all 0.3s ease !important;
                box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            }
            .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
                border-color: #06b6d4 !important;
                box-shadow: 0 0 15px rgba(6, 182, 212, 0.3), inset 0 0 10px rgba(6, 182, 212, 0.1) !important;
                background: rgba(15, 23, 42, 0.9) !important;
            }
            
            /* GLOBAL SUCCESS ANIMATION */
            @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .success-holo {
                background: rgba(6, 182, 212, 0.1);
                border: 1px solid #06b6d4;
                color: #06b6d4;
                padding: 40px;
                text-align: center;
                border-radius: 12px;
                box-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
                animation: fadeIn 0.5s ease-out;
            }
        </style>
    """), unsafe_allow_html=True)

    # 1. NAVBAR
    import components
    components.render_navbar()

    # 2. TITLE SECTION
    st.markdown("""
        <div class="holo-title">CONTACT NODE</div>
        <div class="holo-subtitle">ESTABLISH SECURE CONNECTION // TRANSMISSION READY</div>
    """, unsafe_allow_html=True)

    # 3. CONTACT GRID
    st.markdown("""
        <div class="info-grid">
            <div class="holo-card">
                <div class="holo-icon">📧</div>
                <h3>DIGITAL FREQUENCY</h3>
                <p>support@skillgapai.com</p>
                <p>sales@skillgapai.com</p>
            </div>
            <div class="holo-card">
                <div class="holo-icon">📍</div>
                <h3>PHYSICAL COORDS</h3>
                <p>123 Innovation Drive</p>
                <p>Sector 7, Tech City</p>
            </div>
            <div class="holo-card">
                <div class="holo-icon">📡</div>
                <h3>VOICE UPLINK</h3>
                <p>+91 11111 11111</p>
                <p>09:00 - 18:00 IST</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4. FORM SECTION
    col_spacer_l, col_main, col_spacer_r = st.columns([1, 6, 1])
    
    with col_main:
        # Check submission state
        if "contact_submitted" in st.session_state and st.session_state["contact_submitted"]:
            st.markdown("""
                <div class="success-holo">
                    <div style="font-size: 4rem; margin-bottom: 10px;">🟢</div>
                    <h2 style="font-family:'Orbitron'; margin-bottom:10px;">TRANSMISSION SUCCESSFUL</h2>
                    <p>Your message has been encoded and sent to our operatives.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("REINITIATE UPLINK (New Message)", use_container_width=True):
                st.session_state["contact_submitted"] = False
                st.rerun()
        else:
            with st.form("contact_form"):
                st.markdown("""
                    <h3 style="color:#a855f7; font-family:'Orbitron'; margin-bottom:20px; text-transform:uppercase;">// Compose Message</h3>
                """, unsafe_allow_html=True)
                
                row1_1, row1_2 = st.columns(2)
                with row1_1:
                    first_name = st.text_input("Datastream ID (First Name)", placeholder="Enter Name...")
                with row1_2:
                    last_name = st.text_input("Family Node (Last Name)", placeholder="Enter Last Name...")
                
                email = st.text_input("Comm-Link (Email Address)", placeholder="example@domain.com")
                subject = st.text_input("Packet Header (Subject)", placeholder="Topic of Inquiry...")
                message = st.text_area("Payload Content (Message)", placeholder="Type your message encrypted here...", height=150)
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("INITIATE TRANSFER 🚀", type="primary", use_container_width=True)
                
                if submitted:
                    if not first_name.strip() or not email.strip() or not subject.strip() or not message.strip():
                        st.warning("⚠️ CRITICAL ERROR: All fields (Name, Email, Subject, Message) are mandatory.")
                    elif "@" not in email or "." not in email:
                        st.warning("⚠️ INVALID COMM-LINK: Please enter a valid email address.")
                    else:
                        contact_data = {
                            "name": f"{first_name} {last_name}".strip(),
                            "email": email,
                            "subject": subject,
                            "message": message
                        }
                        
                        with st.status("📡 ESTABLISHING UPLINK...", expanded=True) as status:
                            st.write("Encrypting payload...")
                            time.sleep(1)
                            st.write("Handshaking with server...")
                            success, response = send_contact_email(contact_data)
                            
                            if success:
                                status.update(label="TRANSMISSION COMPLETE", state="complete", expanded=False)
                                st.session_state["contact_submitted"] = True
                                st.balloons()
                                st.rerun()
                            else:
                                status.update(label="UPLINK FAILED", state="error", expanded=True)
                                st.error(f"Error: {response}")
    components.render_footer()

if __name__ == "__main__":
    st.set_page_config(page_title="Contact Us", layout="wide")
    app()
