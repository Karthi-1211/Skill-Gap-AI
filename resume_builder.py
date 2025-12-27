import streamlit as st
import time
import components
import base64
import textwrap
import re
import pdf_gen

# ------------------------------------------------------------------------------
# 1.HELPER FUNCTIONS & RENDERERS
# ------------------------------------------------------------------------------

def get_theme_colors(theme_name):
    """Returns a color dictionary for the selected theme."""
    themes = {
        "Classic Blue": {"primary": "#2563eb", "secondary": "#64748b", "text": "#1e293b", "bg": "#ffffff"},
        "Modern Teal":  {"primary": "#0d9488", "secondary": "#475569", "text": "#0f172a", "bg": "#f0fdfa"},
        "Elegant Dark": {"primary": "#1e293b", "secondary": "#64748b", "text": "#0f172a", "bg": "#f8fafc"},
        "Creative Purple": {"primary": "#7c3aed", "secondary": "#94a3b8", "text": "#2e1065", "bg": "#ffffff"},
        "Academic Red": {"primary": "#be123c", "secondary": "#71717a", "text": "#4c0519", "bg": "#fff1f2"},
    }
    return themes.get(theme_name, themes["Classic Blue"])

def validate_basics_section(cv):
    """Checks if the Basics section is valid. Returns list of errors."""
    errors = []
    if not cv.get("name"): errors.append("Full Name is required.")
    if not cv.get("role"): errors.append("Current Role is required.")
    if not cv.get("email"): errors.append("Email is required.")
    if not cv.get("phone"): errors.append("Phone is required.")
    
    # URL Validation
    github_re = r"^(https?://)?(www\.)?github\.com/[A-Za-z0-9_.-]+/?$"
    linkedin_re = r"^(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?$"
    
    if cv.get("github") and not re.match(github_re, cv["github"]):
        errors.append("Invalid GitHub URL (must be github.com/username)")
    if cv.get("linkedin") and not re.match(linkedin_re, cv["linkedin"]):
        errors.append("Invalid LinkedIn URL (must be linkedin.com/in/username)")
        
    return errors

def generate_ai_suggestions(text, section):
    """Simulates AI suggestions based on heuristics."""
    if not text or len(text) < 10:
        return "⚠️ Content is too short. Please add more details to get valid suggestions."
    
    suggestions = []
    
    # 1. Check for Action Verbs
    action_verbs = ["led", "developed", "created", "managed", "analyzed", "designed", "implemented", "optimized", "achieved"]
    if not any(verb in text.lower() for verb in action_verbs):
        suggestions.append("• Use strong action verbs (e.g., Led, Developed, Optimized) to start sentences.")
        
    # 2. Check for Metrics
    if not re.search(r'\d+%|\d+', text):
        suggestions.append("• Quantify your impact with numbers (e.g., 'Increased revenue by 20%', 'Managed team of 5').")
        
    # 3. Length Check
    if len(text.split()) < 20 and section == "experience":
        suggestions.append("• This description seems brief. Elaborate on your specific responsibilities and achievements.")
        
    if section == "summary":
        if "experienced" not in text.lower() and "passionate" not in text.lower():
             suggestions.append("• Consider mentioning your years of experience and key passion/focus area.")

    if not suggestions:
        return "✅ Excellent! Your content looks strong, using action verbs and metrics."
    
    return "💡 AI Suggestions:\n" + "\n".join(suggestions)

# ------------------------------------------------------------------------------
# 1. HELPERS
# ------------------------------------------------------------------------------

def validate_resume_data(data):
    """
    Validates that all essential fields are filled.
    Returns (True, "") or (False, ErrorMessage).
    """
    if not data.get("name"): return False, "Full Name is required."
    if not data.get("email"): return False, "Email is required."
    if "@" not in data.get("email", ""): return False, "Invalid Email format."
    if not data.get("phone"): return False, "Phone Number is required."
    if not data.get("role"): return False, "Current Role is required."
    if not data.get("summary"): return False, "Professional Summary is required."
    
    # Check for at least one major section content
    has_exp = data.get("experience") and len(data["experience"]) > 0
    has_edu = data.get("education") and len(data["education"]) > 0
    has_proj = data.get("projects") and len(data["projects"]) > 0
    
    if not (has_exp or has_edu or has_proj):
        return False, "Please add at least one entry for Experience, Education, or Projects."
        
    # Deep validation of lists
    if has_exp:
        for i, exp in enumerate(data["experience"]):
            if not exp.get("title") or not exp.get("company"):
                return False, f"Experience #{i+1} is missing Title or Company."
    
    if has_edu:
         for i, edu in enumerate(data["education"]):
             if not edu.get("school") or not edu.get("degree"):
                 return False, f"Education #{i+1} is missing School or Degree."
                 
    return True, ""

def render_preview(data, ui_state):
    """Delegate rendering to the shared PDF generator to ensure 100% visual match."""
    import pdf_gen
    return pdf_gen.render_resume_html(data, ui_state, is_preview=True)

# ------------------------------------------------------------------------------
# 2. MAIN APP
# ------------------------------------------------------------------------------

def app():
    components.render_navbar()
    
    # Initialize UI state wrapper if not present
    if "res_ui_step" not in st.session_state:
        st.session_state["res_ui_step"] = "home" 

    if "prev_res_ui_step" not in st.session_state:
        st.session_state["prev_res_ui_step"] = st.session_state["res_ui_step"] 

    if st.session_state["prev_res_ui_step"] != st.session_state["res_ui_step"]:
        st.session_state["prev_res_ui_step"] = st.session_state["res_ui_step"]
        components.scroll_to_top(smooth=False)

    if "cv_data" not in st.session_state:
        st.session_state["cv_data"] = {
            "name": "",
            "email": "", 
            "phone": "",
            "github": "",
            "linkedin": "",
            "role": "",
            "summary": "",
            "skills": [], 
            "experience": [],
            "education": [],
            "projects": [], 
            "achievements": "",
            "certifications": []
        }
        
    # Initialize Builder Data
    if "builder_data" not in st.session_state:
        st.session_state["builder_data"] = {
            "template": "Ivy League", "theme": "Classic Blue", "zoom": 100, "target_jd": "", "current_version": "V1",
            "section_order": [
                {"key": "summary", "label": "Summary", "enabled": True},
                {"key": "education", "label": "Education", "enabled": True},
                {"key": "skills", "label": "Skills", "enabled": True},
                {"key": "experience", "label": "Experience", "enabled": True},
                {"key": "projects", "label": "Projects", "enabled": True},
                {"key": "achievements", "label": "Achievements", "enabled": True},
                {"key": "certifications", "label": "Certifications", "enabled": True}
            ]
        }
    
    existing_keys = [s["key"] for s in st.session_state["builder_data"]["section_order"]]
    if "achievements" not in existing_keys:
        st.session_state["builder_data"]["section_order"].append({"key": "achievements", "label": "Achievements", "enabled": True})
    if "certifications" not in existing_keys:
        st.session_state["builder_data"]["section_order"].append({"key": "certifications", "label": "Certifications", "enabled": True})
    
    # --- COMMON STYLES ---
    st.markdown("""
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .res-btn-primary {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white; border:none; padding: 12px 30px; border-radius:30px; font-weight:bold; font-size:1.1rem;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3); transition: all 0.3s;
    }
    .res-btn-primary:hover {
        transform: translateY(-3px); box-shadow: 0 15px 30px rgba(59, 130, 246, 0.5);
    }
    .feature-card {
        background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:15px;
        backdrop-filter: blur(10px); transition: all 0.3s; height: 100%;
    }
    .feature-card:hover {
        background: rgba(255,255,255,0.08); transform: translateY(-5px); border-color: rgba(255,255,255,0.2);
    }
    .template-card {
        cursor: pointer; border-radius: 12px; overflow: hidden; border: 2px solid transparent; transition: all 0.3s ease;
        position: relative; background: #0f172a; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .template-card:hover {
        transform: scale(1.03); border-color: #3b82f6; box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2);
    }
    .tpl-badge {
        position: absolute; top: 10px; right: 10px; background: #3b82f6; color: white; padding: 4px 10px; 
        font-size: 0.7rem; border-radius: 20px; font-weight: bold; z-index: 10;
    }
    /* Stepper Styling */
    .step-indicator {
        display: flex; justify-content: center; align-items: center; margin-bottom: 30px;
    }
    .step-dot {
        width: 30px; height: 30px; border-radius: 50%; background: #334155; color: #94a3b8;
        display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 10px;
        transition: all 0.3s;
    }
    .step-dot.active {
        background: #3b82f6; color: white; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); transform: scale(1.1);
    }
    .step-line {
        width: 50px; height: 2px; background: #334155;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- PROGRESS INDICATOR ---
    steps = ["home", "template", "editor", "review"]
    curr_idx = steps.index(st.session_state["res_ui_step"])
    
    if st.session_state["res_ui_step"] != "home":
        st.markdown(f"""
        <div class="step-indicator">
            <div class="step-dot {'active' if curr_idx >= 1 else ''}">1</div>
            <div class="step-line" style="background: {'#3b82f6' if curr_idx >= 2 else '#334155'}"></div>
            <div class="step-dot {'active' if curr_idx >= 2 else ''}">2</div>
            <div class="step-line" style="background: {'#3b82f6' if curr_idx >= 3 else '#334155'}"></div>
            <div class="step-dot {'active' if curr_idx >= 3 else ''}">3</div>
        </div>
        """, unsafe_allow_html=True)

    # --- STEP 1: HOME PAGE ---
    if st.session_state["res_ui_step"] == "home":
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; animation: fadeInUp 0.8s ease-out;">
            <div style="display:inline-block; padding:8px 20px; background:rgba(34, 211, 238, 0.1); border-radius:30px; color:#22d3ee; font-weight:600; font-size:0.9rem; margin-bottom:20px; border:1px solid rgba(34, 211, 238, 0.2);">
                ✨ AI-Powered Resume Builder
            </div>
            <h1 style="font-size: 4.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 25px; background: linear-gradient(to right, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Build Your Legacy.<br>
                <span style="background: linear-gradient(to right, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Land the Job.</span>
            </h1>
            <p style="font-size: 1.3rem; color: #94a3b8; max-width: 700px; margin: 0 auto 50px auto; line-height: 1.6;">
                Create ATS-optimized resumes in minutes. Our AI analyzes job descriptions 
                and tailors your profile to help you stand out from the crowd.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons
        hc1, hc2, hc3 = st.columns([1, 1, 1])
        with hc2:
            if st.button("🚀 Start Building Now", use_container_width=True, type="primary"):
                st.session_state["res_ui_step"] = "template"
                st.rerun()

    # --- STEP 2: TEMPLATE SELECTION ---
    elif st.session_state["res_ui_step"] == "template":
        st.markdown("""
        <div style="text-align:center; margin-bottom:40px; animation: fadeInUp 0.5s;">
            <h2 style="font-size: 2.8rem; font-weight: 800; color:white;">Choose Your Style</h2>
            <p style="color:#94a3b8; font-size:1.1rem;">Select a template to begin. You can switch templates anytime in the preview.</p>
        </div>
        """, unsafe_allow_html=True)
        
        t1, t2, t3, t4 = st.columns(4, gap="large")
        
        # Helper to create template card
        def tpl_card(col, name, badge, color, desc, style_html):
            with col:
                st.markdown(f"""
                <div class="template-card" style="border-color:{color}; height: 100%;">
                    <div class="tpl-badge" style="background:{color}">{badge}</div>
                    {style_html}
                    <div style="padding:15px; text-align:center;">
                        <h4 style="color:white; margin:0; font-size: 1.1rem;">{name}</h4>
                        <p style="font-size:0.8rem; color:#94a3b8; margin:5px 0 0 0;">{desc}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select {name}", use_container_width=True, key=f"btn_{name}"):
                    st.session_state["builder_data"]["template"] = name
                    st.session_state["res_ui_step"] = "editor"
                    st.rerun()

        # 1. Ivy League
        tpl_card(t1, "Ivy League", "Professional", "#000000", "Standard minimal academic layout.", 
                 """<div style="background:#fff; height:250px; padding:15px; color:black; font-family:'Times New Roman'; display:flex; flex-direction:column; text-align:center; border-bottom:1px solid #333;">
                        <div style="text-transform:uppercase; font-size:1rem; border-bottom:1px solid #000; margin-bottom:5px;">Your Name</div>
                        <div style="font-size:0.6rem; text-align:left;"><b>Education</b><br>University of State<br><i>Bachelor of Science</i></div>
                    </div>""")

        # 2. Minimal
        tpl_card(t2, "Minimal", "Classic", "#475569", "Clean serif-based typography.", 
                 """<div style="background:#fff; height:250px; padding:20px; color:#333; font-family:'Inter', sans-serif; display:flex; flex-direction:column; align-items:flex-start;">
                        <div style="font-size:1.2rem; font-weight:800; border-bottom:2px solid #333; margin-bottom:10px; width:50%;">NAME</div>
                        <div style="font-size:0.5rem; color:#666;">Experience<br>Education</div>
                    </div>""")

        # 3. Modern
        tpl_card(t3, "Modern", "Popular", "#2563eb", "Bold header with sleek layout.", 
                 """<div style="background:#fff; height:250px; font-family:'Roboto', sans-serif; display:flex; flex-direction:column;">
                        <div style="background:#2563eb; width:100%; height:80px;"></div>
                        <div style="padding:15px; color:#0f172a;">
                            <div style="font-weight:900; font-size:1.2rem;">NAME</div>
                            <div style="font-size:0.6rem; color:#2563eb; font-weight:bold;">ROLE</div>
                        </div>
                    </div>""")

        # 4. Creative
        tpl_card(t4, "Creative", "Vibrant", "#7c3aed", "Unique sidebar and visual pop.", 
                 """<div style="background:#fff; height:250px; display:flex; font-family:'Poppins', sans-serif;">
                        <div style="background:#7c3aed; width:35%; height:100%;"></div>
                        <div style="width:65%; padding:15px; display:flex; flex-direction:column; justify-content:center;">
                             <div style="font-weight:bold; color:#7c3aed; font-size:1rem;">NAME</div>
                             <div style="font-size:0.5rem;">Creative Portfolio</div>
                        </div>
                    </div>""")
        
        st.markdown("<br><div style='text-align:center;'>", unsafe_allow_html=True)
        if st.button("⬅ Back to Home"):
            st.session_state["res_ui_step"] = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- STEP 3: LIVE EDITOR ---
    elif st.session_state["res_ui_step"] == "editor":
        # Load Data
        cv = st.session_state["cv_data"]
        ui = st.session_state["builder_data"]
        
        # Top Bar
        c_title, c_actions = st.columns([2, 1])
        with c_title:
             st.markdown(f"### 📝 Editing: {ui['template']} Resume")
        with c_actions:
             if st.button("Preview & Download ➡", type="primary", use_container_width=True):
                 valid, msg = validate_resume_data(cv)
                 if valid:
                     st.session_state["res_ui_step"] = "review"
                     st.rerun()
                 else:
                     st.error(f"❌ {msg}")
        
        # Split Layout: Left (Form) - Right (Preview)
        col_form, col_view = st.columns([1, 1], gap="large")
        
        with col_form:
            tabs = st.tabs(["👤 Basics", "💼 Experience", "🎓 Education", "🚀 Projects", "🛠 Skills", "🏆 Achievements", "📜 Certifications"])
            
            with tabs[0]: # Basics
                with st.expander("Personal Details", expanded=True):
                    c1, c2 = st.columns(2)
                    cv["name"] = c1.text_input("Full Name *", cv["name"], placeholder="e.g. John Doe")
                    cv["role"] = c2.text_input("Current Role", cv["role"], placeholder="e.g. Software Engineer")
                    
                    c3, c4 = st.columns(2)
                    cv["email"] = c3.text_input("Email *", cv["email"], placeholder="john@example.com")
                    cv["phone"] = c4.text_input("Phone *", cv["phone"], placeholder="(555) 123-4567")

                    # Live Validation
                    if not cv["name"]: st.error("Name is required.")
                    if not cv["email"]: st.error("Email is required.")
                    if not cv["phone"]: st.error("Phone is required.")
                    
                    c5, c6 = st.columns(2)
                    cv["github"] = c5.text_input("GitHub URL", cv.get("github", ""), placeholder="github.com/johndoe")
                    cv["linkedin"] = c6.text_input("LinkedIn URL", cv.get("linkedin", ""), placeholder="linkedin.com/in/johndoe")
                    
                    if st.button("💾 Save Basics"):
                        # Validation Logic
                        errors = validate_basics_section(cv)
                        if errors:
                            for e in errors:
                                st.error(f"❌ {e}")
                        else:
                            st.success("✅ Basics saved successfully! You can now move to the Experience section.")


                
                with st.expander("Professional Summary", expanded=True):
                    cv["summary"] = st.text_area("Summary", cv["summary"], height=120, placeholder="Brief overview of your career...")
                    c1, c2 = st.columns([1, 3])
                    with c1: 
                        if st.button("💾 Save Summary"): pass
                    with c2:
                        if st.button("✨ AI Suggest Improvements", key="ai_sum"):
                            sugg = generate_ai_suggestions(cv["summary"], "summary")
                            st.info(sugg)

            with tabs[1]: # Experience
                if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Experience.")
                else:
                    for i, exp in enumerate(cv["experience"]):
                        with st.expander(f"{exp['title'] or 'Role ' + str(i+1)}", expanded=False):
                            exp["title"] = st.text_input(f"Job Title", exp["title"], key=f"t{i}")
                            exp["company"] = st.text_input(f"Company", exp["company"], key=f"c{i}")
                            exp["duration"] = st.text_input(f"Duration", exp["duration"], key=f"dur{i}", placeholder="Jan 2020 - Present")
                            exp["desc"] = st.text_area(f"Description (Use newlines for bullets)", exp["desc"], key=f"d{i}", height=120)
                            
                            c1, c2, c3 = st.columns([1, 1, 1])
                            with c1:
                                if st.button(f"💾 Save", key=f"sv_exp_{i}"): pass
                            with c2:
                                if st.button(f"✨ AI Suggest", key=f"ai_exp_{i}"):
                                    sugg = generate_ai_suggestions(exp["desc"], "experience")
                                    st.info(sugg)
                            with c3:   
                                if st.button(f"🗑 Delete", key=f"del_exp_{i}"):
                                    cv["experience"].pop(i)
                                    st.rerun()
                    if st.button("➕ Add Experience"):
                        cv["experience"].append({"title":"", "company":"", "desc": "", "duration": ""})
                        st.rerun()

            with tabs[2]: # Education
                 if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Education.")
                 else:
                     for i, edu in enumerate(cv["education"]):
                        with st.expander(f"{edu['school'] or 'School ' + str(i+1)}", expanded=False):
                            edu["school"] = st.text_input(f"School/University", edu["school"], key=f"eds{i}")
                            edu["degree"] = st.text_input(f"Degree", edu["degree"], key=f"edd{i}", placeholder="B.S. Computer Science")
                            edu["year"] = st.text_input(f"Year", edu["year"], key=f"edy{i}",placeholder="Jan 2020 - Present")
                            c1, c2 = st.columns([1, 1])
                            with c1:
                                 if st.button(f"💾 Save", key=f"sv_edu_{i}"): pass
                            with c2:
                                if st.button(f"🗑 Delete", key=f"del_edu_{i}"):
                                    cv["education"].pop(i)
                                    st.rerun()
                     if st.button("➕ Add Education"):
                        cv["education"].append({"degree": "", "school": "", "year": "", "location": ""})
                        st.rerun()

            with tabs[3]: # Projects
                 if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Projects.")
                 else:
                     for i, proj in enumerate(cv.get("projects", [])):
                        with st.expander(f"{proj['title'] or 'Project ' + str(i+1)}", expanded=False):
                            proj["title"] = st.text_input(f"Project Title", proj["title"], key=f"pt{i}")
                            proj["tech"] = st.text_input(f"Tech Stack", ", ".join(proj.get("tech", [])), key=f"ptech{i}", placeholder="Python, React...").split(",")
                            proj["desc"] = st.text_area(f"Description", proj["desc"], key=f"pd{i}")
                            c1, c2 = st.columns([1, 1])
                            with c1:
                                 if st.button(f"💾 Save", key=f"sv_proj_{i}"): pass
                            with c2:
                                if st.button(f"🗑 Delete", key=f"del_proj_{i}"):
                                    cv["projects"].pop(i)
                                    st.rerun()
                     if st.button("➕ Add Project"):
                         cv.setdefault("projects", []).append({"title": "", "tech": [], "desc": ""})
                         st.rerun()

            with tabs[4]: # SKILLS
                if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Skills.")
                else:
                    st.markdown("Add skills with categories (e.g., **Languages**: Python, Java) or just a list.")
                    
                    if st.button("➕ Add Skill Category"):
                        # Normalization to lists of dicts
                        if not cv["skills"]: cv["skills"] = []
                        if cv["skills"] and isinstance(cv["skills"][0], str):
                             cv["skills"] = [{"category": "General", "items": ", ".join(cv["skills"])}]
                        
                        cv["skills"].append({"category": "", "items": ""})
                        st.rerun()

                    # Render
                    if cv["skills"] and isinstance(cv["skills"][0], str):
                         st.warning("Legacy format detected. Saving will convert to categories.")
                         flat_skills = ", ".join(cv["skills"])
                         new_flat = st.text_area("Skills (comma separated)", flat_skills)
                         cv["skills"] = [s.strip() for s in new_flat.split(",") if s.strip()]
                    else:
                        for i, sk in enumerate(cv["skills"]):
                             with st.container():
                                 c1, c2, c3 = st.columns([1, 2, 0.5])
                                 sk["category"] = c1.text_input("Category (e.g. Tools)", sk.get("category",""), key=f"cat_{i}")
                                 sk["items"] = c2.text_input("Skills", sk.get("items",""), key=f"itm_{i}")
                                 if c3.button("🗑", key=f"del_sk_{i}"):
                                     cv["skills"].pop(i)
                                     st.rerun()

            with tabs[5]: # ACHIEVEMENTS
                 if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Achievements.")
                 else:
                     st.info("💡 Highlight key awards, competitions, or recognition.")
                     cv["achievements"] = st.text_area("Achievements", cv.get("achievements", ""), height=150, placeholder="• Won 1st place in National Hackathon\n• Awarded Employee of the Month")

            with tabs[6]: # CERTIFICATIONS
                 if validate_basics_section(cv):
                     st.warning("🔒 Please fill out the **Basics** section correctly before adding Certifications.")
                 else:
                     if st.button("➕ Add Certification"):
                         cv.setdefault("certifications", []).append({"name": "", "authority": "", "year": ""})
                         st.rerun()
                     
                     for i, cert in enumerate(cv.get("certifications", [])):
                         with st.container():
                             c_h1, c_h2 = st.columns([3, 1])
                             cert["name"] = c_h1.text_input("Certificate Name *", cert["name"], key=f"cn{i}", placeholder="AWS Certified Solutions Architect")
                             cert["year"] = c_h2.text_input("Year", cert["year"], key=f"cy{i}", placeholder="2023")
                             cert["authority"] = st.text_input("Issuing Authority", cert["authority"], key=f"ca{i}", placeholder="Amazon Web Services")
                             
                             if not cert["name"]:
                                 st.caption("⚠️ Name is required for this certificate to appear.")
                                 
                             if st.button("🗑 Remove Cert", key=f"del_crt_{i}"):
                                 cv["certifications"].pop(i)
                                 st.rerun()
        
        # Save Progress Logic
        components.save_progress()

        with col_view:
            st.markdown("#### Only Preview")
            html_out = render_preview(cv, ui)
            st.components.v1.html(html_out, height=800, scrolling=True)


    # --- STEP 4: FINAL PREVIEW & DOWNLOAD ---
    elif st.session_state["res_ui_step"] == "review":
        cv = st.session_state["cv_data"]
        ui = st.session_state["builder_data"]

        # Toolbar
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅ Back to Edit"):
                st.session_state["res_ui_step"] = "editor"
                st.rerun()
        
        with c2:
            st.markdown("#### 🎨 Switch Template (Live)")
            new_tmpl = st.selectbox("", ["Ivy League", "Minimal", "Modern", "Creative"], label_visibility="collapsed", key="final_review_tmpl_select")
            if new_tmpl != ui["template"]:
                ui["template"] = new_tmpl
                st.rerun()
                
        with c3: 
             pdf_gen_html = pdf_gen.get_client_side_pdf_html(cv, ui["template"])
             b64_gen = base64.b64encode(pdf_gen_html.encode()).decode()
             
             href_pdf = f'<a href="data:text/html;base64,{b64_gen}" download="{cv["name"].replace(" ", "_")}_Generate_PDF.html" style="text-decoration:none;">'
             href_pdf += '<button style="background-color:#FF4B4B; color:white; border:none; padding: 10px 20px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">📥 Download PDF (Highest Quality)</button>'
             href_pdf += '</a>'
             
             st.markdown(href_pdf, unsafe_allow_html=True)
             st.caption("Click to download the PDF generator. Open it to auto-save your perfect PDF.")

             # 2. HTML Backup
             html_final = render_preview(cv, ui)
             b64 = base64.b64encode(html_final.encode()).decode()
             href = f'<a href="data:text/html;base64,{b64}" download="{cv["name"].replace(" ", "_")}_Resume_Web.html" style="margin-top:10px; display:block; text-align:center; font-size:0.8rem; color:#666; text-decoration:none;">Download Raw HTML</a>'
             st.markdown(href, unsafe_allow_html=True)
             
        st.divider()
        st.subheader("Document Preview (Web View)")
        st.components.v1.html(render_preview(cv, ui), height=1000, scrolling=True)
        components.save_progress()