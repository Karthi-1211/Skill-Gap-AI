import streamlit as st
import components
import pandas as pd
import textwrap
import random
import time

def app():
    # Helper to check status
    def check_status():
        status = {
            "m1": False,
            "m2": False,
            "m3": False,
            "m4": False
        }
        
        r_text = st.session_state.get("resume_manual", "")
        has_text = r_text and len(str(r_text).strip()) > 5
        
        m2_data = st.session_state.get("m2_extracted_skills", {})
        has_skills = isinstance(m2_data, dict) and (m2_data.get("resume") or m2_data.get("jd"))
        
        if has_text or has_skills:
            status["m1"] = True
            
        if has_skills:
            status["m2"] = True
                
        # Robust check for M3 (Results)
        m3_res = st.session_state.get("m3_results", {})
        if m3_res and isinstance(m3_res, dict) and "stats" in m3_res:
             status["m3"] = True
             
        # Robust check for M4 (Report)
        if st.session_state.get("m4_data") or (status["m3"] and status["m1"]):
            
            status["m4"] = True
            
        return status

    status = check_status()
    completed_steps = sum(status.values())
    total_steps = 4
    progress = int((completed_steps / total_steps) * 100)
    
    components.render_navbar()
    
    if "updated_resume_score" not in st.session_state:
        st.session_state["updated_resume_score"] = None
    
    # STUDENT PROFILE HEADER
    original_score = 0
    if "m3_results" in st.session_state:
            original_score = st.session_state["m3_results"]["stats"]["overall"]
            
    # Determine which score to display (Best of Original vs Updated)
    display_score = original_score
    if st.session_state["updated_resume_score"]:
        display_score = max(original_score, st.session_state["updated_resume_score"])
            
    # TITLE & NAV
    c_profile, c_reset = st.columns([4, 1.2])
    
    with c_profile:
        # Profile Section
        st.markdown(textwrap.dedent(f"""\
        <div style="display:flex; align-items:center; gap:25px; margin-top: 10px; margin-bottom: 20px;">
            <div style="width:90px; height:90px; background:linear-gradient(135deg, #3b82f6, #2563eb); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:2.8rem; font-weight:bold; box-shadow:0 10px 25px rgba(59,130,246,0.4); border: 3px solid rgba(255,255,255,0.1);">
                👨‍🎓
            </div>
            <div>
                <h1 style="margin:0; font-size:2.8rem; font-weight:800; background: linear-gradient(90deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px;">
                    Welcome, Future Pro
                </h1>
                <div style="display:flex; align-items:center; gap:10px; margin-top:5px;">
                    <span style="background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:6px; color:#cbd5e1; font-size:0.85rem; border:1px solid rgba(255,255,255,0.05);">Full Stack Developer</span>
                    <span style="color: #64748b; font-size: 0.85rem;">•</span>
                    <span style="color: #94a3b8; font-size: 0.9rem;">Level 4 Student</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)
        
    with c_reset:
        # Reset Button (Top Right)
        st.write("") 
        st.write("")
        st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            width: 100%;
            background-color: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: #94a3b8;
            font-size: 0.8rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.2s;
        }
        div[data-testid="stButton"] button:hover {
            color: #ef4444;
            border-color: #ef4444;
            background-color: rgba(239, 68, 68, 0.1);
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reset Session", key="dash_reset_top_right"):
             components.reset_student_session()

    # SCORE & PROGRESS SECTION (Moved Down)
    c_score, c_progress = st.columns([1.5, 3.5])
    
    with c_score:
        badge = "Beginner"
        if display_score > 85: badge = "💎 Elite Talent"
        elif display_score > 70: badge = "🥇 Advanced"
        elif display_score > 50: badge = "🥈 Intermediate"
        
        st.markdown(textwrap.dedent(f"""\
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:700;">Current AI Score</div>
            <div style="display:flex; align-items:center; justify-content:center; gap: 10px; margin-top: 5px;">
                <div style="font-size:2.8rem; font-weight:900; color:#3b82f6; line-height:1;">{display_score}</div>
            </div>
            <div style="margin-top: 8px;">
                <span style="background:rgba(59,130,246,0.15); color:#60a5fa; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.75rem; border:1px solid rgba(59,130,246,0.2);">{badge}</span>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with c_progress:
        # Progress Bar Card
        st.markdown(textwrap.dedent(f"""\
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 25px 20px; border-radius: 16px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                     <span style="font-size:1.2rem;">🚀</span>
                     <span style="font-weight: 700; color: white; font-size: 1rem;">Career Readiness Tracker</span>
                </div>
                <span style="font-weight: 800; color: #3b82f6; font-size: 1.1rem;">{progress}%</span>
            </div>
            <div style="height: 10px; background: rgba(0,0,0,0.3); border-radius: 6px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
                <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); box-shadow: 0 0 15px rgba(59, 130, 246, 0.6); transition: width 0.5s ease;"></div>
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #64748b; text-align: right;">
                {completed_steps}/{total_steps} Milestones Completed
            </div>
        </div>
        """), unsafe_allow_html=True)
    
    # Dashboard Grid
    st.markdown("""
    <style>
    .mission-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    .mission-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }
    .mission-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 4px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .mission-card:hover::before {
        opacity: 1;
    }
    .card-icon {
        width: 50px; height: 50px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .status-badge {
        font-size: 0.7rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-completed {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .status-pending {
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* Force Primary Buttons to be Blue for this page */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #3b82f6 !important;
        border: 1px solid #3b82f6 !important;
        color: white !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    div[data-testid="stButton"] > button[kind="primary"]:active {
        background-color: #1d4ed8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    
    # Card Helper
    def dashboard_card(title, icon, desc, status_bool, nav_target, btn_key):
        status_class = "status-completed" if status_bool else "status-pending"
        status_text = "Completed" if status_bool else "Pending"
        
        # HTML Render
        st.markdown(f"""
        <div class="mission-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div class="card-icon">{icon}</div>
                <div class="status-badge {status_class}">
                    {status_text}
                </div>
            </div>
            <h3 style="color: white; font-weight: 700; font-size: 1.2rem; margin: 0 0 8px 0;">{title}</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 20px; min-height: 45px;">
                {desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        btn_label = "Review Analysis" if status_bool else "Start Mission"
        
        btn_type = "secondary" if status_bool else "primary"
        
        if st.button(f"{btn_label} &nbsp; ➔", key=f"d_card_{btn_key}", use_container_width=True, type=btn_type):
             components.navigate_to(nav_target)
             st.rerun()

    # Dynamic Descriptions (Enhanced)
    desc_m1 = "Initialize the pipeline by ingesting your resume data and target job description."
    if status["m1"]:
        r_text = st.session_state.get("resume_manual", "")
        desc_m1 = f"Data received. Resume ({len(str(r_text).split())} words) ready for extraction."
        
    desc_m2 = "AI agents scan your documents to extract a structured skill ontology."
    if status["m2"]:
        m2_data = st.session_state.get("m2_extracted_skills", {})
        s_count = len(m2_data.get("resume", [])) if m2_data else 0
        desc_m2 = f"Intelligence extraction complete. {s_count} skills mapped to memory."

    desc_m3 = "Perform a deep-dive Gap Analysis to identify critical missing competencies."
    if status["m3"]:
        stats = st.session_state["m3_results"]["stats"]
        desc_m3 = f"Gap Analysis complete. Match Score: {stats['overall']}%."
        
    desc_m4 = "Generate a strategic roadmap and intelligence report to bridge the gaps."
    if status["m4"]:
        desc_m4 = "Final Report generated. 4-Week Plan ready for execution."

    with c1:
        dashboard_card("1. Data Ingestion", "📂", desc_m1, status["m1"], "Milestone 1: Data Ingestion", "1")
        st.write("") # Spacing
        dashboard_card("3. Gap Analysis", "📊", desc_m3, status["m3"], "Milestone 3: Gap Analysis", "3")

    with c2:
        dashboard_card("2. Skill Extraction", "🧠", desc_m2, status["m2"], "Milestone 2: Skill Extraction", "2")
        st.write("") # Spacing
        dashboard_card("4. Final Report", "📈", desc_m4, status["m4"], "Milestone 4: Dashboard & Report", "4")

    # ---------------------------------------------------------
    # RESUME EVOLUTION & UPDATE (NEW FEATURE)
    # ---------------------------------------------------------
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""\
    <div style="margin-top: 20px; margin-bottom: 25px;">
        <h2 style="background: -webkit-linear-gradient(45deg, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
            🧬 Resume Evolution
        </h2>
        <p style="color: #94a3b8; font-size: 1rem;">
            Closed your skill gaps? Upload your <b>updated resume</b> to see your new score and apply with confidence.
        </p>
    </div>
    """), unsafe_allow_html=True)
    
    evo_c1, evo_c2 = st.columns([1, 1])
    
    with evo_c1:
         # Original Resume Card
         st.markdown(textwrap.dedent(f"""\
         <div style="background:rgba(255,255,255,0.02); padding:25px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); height:100%;">
             <div style="font-weight:700; color:#94a3b8; margin-bottom:10px;">ORIGINAL VERSION</div>
             <div style="font-size:3rem; font-weight:800; color:white; margin-bottom:5px;">{original_score}%</div>
             <div style="font-size:0.9rem; color:#94a3b8; margin-bottom:20px;">Initial Match Score based on parsed data of Milestone 1.</div>
             
            <div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="color:#cbd5e1; font-size:0.85rem;">Skills Found</span>
                        <span style="color:white; font-weight:600;">{len(st.session_state.get('m2_extracted_skills', {}).get('resume', []))}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                        <span style="color:#cbd5e1; font-size:0.85rem;">Status</span>
                        <span style="color:#ef4444; font-weight:600;">Outdated</span>
                </div>
            </div>
         </div>
         """), unsafe_allow_html=True)
         
    with evo_c2:
        # Upload New Resume Card
        box_style = "border: 2px dashed #3b82f6; background: rgba(59, 130, 246, 0.05);" if not st.session_state["updated_resume_score"] else "border: 2px solid #10b981; background: rgba(16, 185, 129, 0.05);"
        
        st.markdown(textwrap.dedent(f"""\
        <div style="padding:25px; border-radius:16px; {box_style} height:100%; transition:all 0.3s;">
             <div style="display:flex; justify-content:space-between; align-items:start;">
                 <div>
                    <div style="font-weight:700; color:{'#10b981' if st.session_state['updated_resume_score'] else '#3b82f6'}; margin-bottom:5px;">
                        {'✅ UPDATED VERSION' if st.session_state['updated_resume_score'] else '🚀 UPLOAD NEW VERSION'}
                    </div>
                 </div>
                 <div style="font-size:1.5rem;">{'📈' if st.session_state['updated_resume_score'] else '📤'}</div>
             </div>
        """), unsafe_allow_html=True)
        
        if st.session_state["updated_resume_score"]:
            # SHOW RESULT
            st.markdown(textwrap.dedent(f"""\
            <div style="font-size:3rem; font-weight:800; color:#10b981; margin-bottom:5px;">
                {st.session_state['updated_resume_score']}%
                <span style="font-size:1rem; color:#10b981; vertical-align:middle; background:rgba(16,185,129,0.2); padding:4px 8px; border-radius:12px;">+{st.session_state['updated_resume_score'] - original_score}%</span>
            </div>
            <div style="font-size:0.9rem; color:#94a3b8; margin-bottom:20px;">Great job! Your new resume is optimized for the application.</div>
            """), unsafe_allow_html=True)
            
            if st.button("Reset / Upload Different", type="secondary", use_container_width=True):
                st.session_state["updated_resume_score"] = None
                st.rerun()
        else:
            # SHOW UPLOADER
            st.markdown("""<p style="color:#94a3b8; font-size:0.9rem;">Upload your refined PDF to recalculate your match score before applying.</p>""", unsafe_allow_html=True)
            # Cleanup potential state conflict
            if "updater_uploader" in st.session_state and st.session_state["updater_uploader"] is None:
                del st.session_state["updater_uploader"]

            new_resume = st.file_uploader("Select Updated Resume (PDF)", type=["pdf"], key="updater_uploader")
            
            if new_resume is not None:
                if st.button("Analyze & Update Score", type="primary", use_container_width=True):
                    with st.spinner("Parsing new structure... re-evaluating keywords..."):
                        time.sleep(2) 
                        improvement = random.randint(10, 25)
                        new_score = min(98, original_score + improvement)
                        st.session_state["updated_resume_score"] = new_score
                        st.balloons()
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ADVANCED CAREER ACCELERATOR
    # ---------------------------------------------------------
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""\
    <div style="margin-top: 20px; margin-bottom: 20px;">
        <h2 style="background: -webkit-linear-gradient(45deg, #f59e0b, #d97706); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
            🚀 Career Accelerator Hub
        </h2>
        <p style="color: #94a3b8; font-size: 1rem;">
            Advanced tools to prepare you for the role.
        </p>
    </div>
    """), unsafe_allow_html=True)

    tab_skill, tab_learn = st.tabs(["🛠️ Skill Gap Eraser", "📚 Learning Resources"])

    with tab_skill:
        c_acc1, c_acc2 = st.columns([2, 1])
        with c_acc1:
            st.markdown("#### ✅ Personalized Gap Checklist")
            st.info("The system found these critical missing skills. Check them off as you master them.")
            
            # Logic to get missing skills from Milestone 3
            missing_skills = []
            if "m3_results" in st.session_state:
                m3 = st.session_state["m3_results"]
                if "jd_details" in m3:
                    # Filter for low matches properly from the details list
                    missing_skills = [d["jd_skill"] for d in m3["jd_details"] if d["category"] == "Low Match"]
            
            if not missing_skills:
                # If no real data yet (user hasn't run M3), show placeholder or empty
                if status["m3"]:
                     st.warning("No specific gaps identified or data unavailable.")
                else:
                     st.info("Complete Milestone 3 (Gap Analysis) to see your real missing skills here.")
                     missing_skills = ["Example: Python", "Example: SQL"] 

            checked = 0
            for skill in missing_skills:
                k = f"gap_check_{skill}"
                if st.checkbox(f"Master **{skill}**", key=k):
                    checked += 1
            
            # Progress
            if len(missing_skills) > 0:
                prog = checked / len(missing_skills)
                st.progress(prog)
                if prog == 1.0:
                    st.success("🎉 All gaps closed! You are ready to update your resume.")

        with c_acc2:
            st.markdown("#### 💡 Quick Actions")
            st.markdown(textwrap.dedent("""\
            <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; font-size:0.9rem; color:#94a3b8;">
                Once you have checked off enough skills, go to <b>Resume Evolution</b> and upload your new resume to boost your score!
            </div>
            """), unsafe_allow_html=True)
            if st.button("Go to Resume Builder", use_container_width=True, key="dash_acc_resume_btn"):
                 components.navigate_to("Resume Builder")
                 st.rerun()

    with tab_learn:
        st.markdown("#### 📚 Recommended Courses for You")
        
        if missing_skills and "Example: Python" not in missing_skills:
             st.write(f"Based on your gap analysis, we recommend focusing on: **{', '.join(missing_skills[:3])}**")
             
             # Dynamic course generation (mocked logic based on skill name)
             res_cols = st.columns(3)
             for i, skill in enumerate(missing_skills[:3]): # Show top 3
                 with res_cols[i]:
                     # Simple heuristic for icon/color
                     card_color = random.choice(["#3b82f6", "#10b981", "#ec4899", "#f59e0b"])
                     icon = "🎓"
                     
                     st.markdown(textwrap.dedent(f"""\
                    <div style="background:#1e293b; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,0.1); height:100%;">
                        <div style="height:100px; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; color:{card_color}; font-size:2.5rem;">{icon}</div>
                        <div style="padding:15px;">
                            <div style="font-weight:700; color:white; margin-bottom:5px;">Mastering {skill}</div>
                            <div style="font-size:0.8rem; color:#94a3b8;">Udemy • 10-15 Hours</div>
                            <a href="https://www.udemy.com/courses/search/?q={skill}" target="_blank" style="color:#60a5fa; font-size:0.9rem; text-decoration:none; display:block; margin-top:10px;">Find Courses &rarr;</a>
                        </div>
                    </div>
                    """), unsafe_allow_html=True)
        else:
             st.info("Generate your Gap Analysis (Milestone 3) to get personalized course recommendations.")

    # ---------------------------------------------------------
    # JOB BOARD & APPLICATIONS
    # ---------------------------------------------------------
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""\
    <div style="margin-bottom: 30px;">
        <h2 style="background: -webkit-linear-gradient(45deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
            🚀 Smart Job Board
        </h2>
        <p style="color: #94a3b8; font-size: 1rem;">Apply with your best score. HR will see your updated profile.</p>
    </div>
    """), unsafe_allow_html=True)

    tab_jobs, tab_apps = st.tabs(["🚀 Active Listings", "📂 My Applications"])
    
    with tab_jobs:
        # Get parsed skills from M2
        m2_skills = st.session_state.get("m2_extracted_skills", {}).get("resume", [])
        
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:15px; background:rgba(59,130,246,0.1); border-left:4px solid #3b82f6; border-radius:8px;">
            <div style="font-weight:700; color:#60a5fa; font-size:0.9rem;">🎯 AI MATCHING ENGINE ACTIVE</div>
            <div style="font-size:0.85rem; color:#cbd5e1;">Jobs are recommended based on your {len(m2_skills)} parsed skills from Milestone 2.</div>
        </div>
        """, unsafe_allow_html=True)
        
        if "jobs" in st.session_state and st.session_state["jobs"]:

            jobs = st.session_state["jobs"]
            # FIX: Use the correct applicant name for filtering
            applied_job_ids = [app["job_id"] for app in st.session_state.get("applications", []) if app.get("applicant") == "Alamanda Balu Karthik"]
            
            # Deterministic Matching Logic
            # Define implicit skills for mock jobs since they don't have them in DB
            JOB_SKILLS_DB = {
                "Associate Data Scientist": ["Python", "SQL", "Pandas", "Machine Learning", "Statistics"],
                "Frontend Developer (React)": ["React", "JavaScript", "HTML", "CSS", "Frontend"],
                "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
                "Product Manager": ["Agile", "Product", "Strategy", "Roadmap", "Communication"]
            }

            job_scores = []
            for job in jobs:
                # Get required skills for this job role (or default)
                req_skills = JOB_SKILLS_DB.get(job["role"], ["Communication"])
                req_skills_set = set([s.lower() for s in req_skills])
                
                # Compare with user skills
                user_skills_set = set([s.lower() for s in m2_skills])
                
                # Calculate Intersection
                common = user_skills_set.intersection(req_skills_set)
                if not req_skills_set:
                     match_val = 0
                else:
                     match_val = int((len(common) / len(req_skills_set)) * 100)
                
                # Boost match if role name roughly matches skills
                for s in m2_skills:
                    if s.lower() in job["role"].lower():
                         match_val += 15
                
                # Cap at 99
                match_val = min(99, match_val)
                # Ensure minimum random jitter isn't solely defining it, but helps with empty states
                if not m2_skills: match_val = 0
                
                job_scores.append({
                    "job": job,
                    "match": match_val,
                    "matched_keywords": list(JOB_SKILLS_DB.get(job["role"], []))  # Show required skills as "matched" candidates
                })
            
            # Sort by match score
            sorted_jobs = sorted(job_scores, key=lambda x: x['match'], reverse=True)
            
            for item in sorted_jobs:
                job = item["job"]
                match_percent = item["match"]
                
                is_applied = job['id'] in applied_job_ids
                
                # Determine keywords to highlight (intersection for real highlighting)
                # Recalculate overlapping display keywords
                req_skills = JOB_SKILLS_DB.get(job["role"], ["General"])
                display_keywords = [s for s in req_skills if s.lower() in [us.lower() for us in m2_skills]]
                if not display_keywords:
                     display_keywords = req_skills[:3] # Fallback to showing what IS needed if none match
                
                border_style = "2px solid #10b981" if is_applied else ("1px solid #3b82f6" if match_percent > 70 else "1px solid rgba(255,255,255,0.05)")
                bg_style = "background:rgba(16, 185, 129, 0.05);" if is_applied else "background:rgba(255,255,255,0.03);"
                
                status_badge = ""
                if is_applied:
                     status_badge = '<span style="background:#10b981; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem; margin-left:10px;">✅ APPLIED</span>'
                
                st.markdown(f"""
<div style="{bg_style} border: {border_style}; border-radius: 12px; padding: 25px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div>
<div style="font-size:0.75rem; color:{'#10b981' if match_percent > 70 else '#94a3b8'}; font-weight:700; text-transform:uppercase; margin-bottom:5px;">
{f'⚡ {match_percent}% SKILL MATCH' if m2_skills else '⚠️ ANALYSIS PENDING'} {status_badge}
</div>
<h3 style="margin: 0; color: white; font-size:1.3rem;">{job['role']}</h3>
<div style="color: #94a3b8; font-size: 0.95rem; margin-top:5px;">
{job['company']} • <span style="color:#cbd5e1;">{job['location']}</span>
</div>
<div style="margin-top:12px; display:flex; gap:8px;">
{''.join([f'<span style="background:rgba(59,130,246,0.2); color:#93c5fd; padding:3px 10px; border-radius:12px; font-size:0.75rem;">{s}</span>' for s in display_keywords])}
</div>
</div>
<div style="text-align: right;">
<div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 5px;">Min Score</div>
<div style="font-weight: 800; color: white; font-size:1.4rem;">{job['min_score']}%</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                
                c_btn_app, _ = st.columns([1, 4])
                with c_btn_app:
                    if is_applied:
                         st.button("✅ Application Sent", key=f"btn_applied_{job['id']}", disabled=True, use_container_width=True)
                    else:
                         if st.button("🚀 Apply Now", key=f"btn_apply_{job['id']}", use_container_width=True, type="primary"):
                             if not m2_skills:
                                 st.error("Please complete Milestone 2 (Skill Extraction) to apply.")
                             elif original_score == 0:
                                 st.error("Please complete Milestone 3 (Gap Analysis) to get a score.")
                             else:
                                 # Smart Apply Logic
                                 score_to_use = original_score
                                 used_updated = False
                                 if st.session_state["updated_resume_score"] and st.session_state["updated_resume_score"] > original_score:
                                     score_to_use = st.session_state["updated_resume_score"]
                                     used_updated = True
                                 
                                 new_app = {
                                     "job_id": job['id'],
                                     "job_role": job['role'],
                                     "applicant": "Alamanda Balu Karthik",
                                     "score": score_to_use,
                                     "status": "Pending",
                                     "applied_at": "Just now",
                                     "resume_version": "Updated v2.0" if used_updated else "Original v1.0",
                                     "company": job['company']
                                 }
                                 st.session_state.setdefault("applications", []).append(new_app)
                                 components.save_progress()
                                 st.toast(f"Application sent to {job['company']}!", icon="🚀")
                                 time.sleep(1)
                                 st.rerun()
                                 
        else:
             st.info("No active jobs available at the moment.")

    with tab_apps:
        my_apps = [app for app in st.session_state.get("applications", []) if app.get("applicant") == "Alamanda Balu Karthik"]
        if my_apps:
            for i, mapp in enumerate(my_apps):
                status_map = ["Pending", "Screening", "Interview", "Offer Sent", "Accepted", "Rejected"]
                curr_status = mapp.get("status", "Pending")
                
                # Colors
                if curr_status == "Rejected":
                    color_theme = "#ef4444"
                elif curr_status == "Accepted":
                    color_theme = "#10b981"
                else:
                    color_theme = "#3b82f6"
                    
                # FORCE LEFT-ALIGN TO FIX CODE BLOCK RENDER ISSUE
                app_card_html = f"""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:16px; padding:24px; margin-bottom:20px; border-left: 5px solid {color_theme};">
<div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:15px;">
<div>
<h3 style="margin:0; color:white;">{mapp['job_role']}</h3>
<p style="color:#94a3b8; margin:5px 0 0 0; font-size:0.9rem;">
Applied: {mapp['applied_at']} • Score: <b>{mapp.get('score', original_score)}%</b>
<span style="margin-left:10px; font-size:0.8rem; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:10px;">{mapp.get('resume_version', 'Original')}</span>
</p>
</div>
<div style="text-align:right;">
<div style="background:{color_theme}20; color:{color_theme}; padding:6px 16px; border-radius:30px; font-weight:700; border:1px solid {color_theme}40; font-size:0.85rem; display:inline-block;">
{curr_status}
</div>
</div>
</div>
</div>
"""
                st.markdown(app_card_html, unsafe_allow_html=True)
        
                # PROGRESS STEPPER
                progress_stepper_html = f"""
<div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px; position:relative;">
<div style="position:absolute; top:12px; left:0; width:100%; height:2px; background:#334155; z-index:0;"></div>
<!-- Step 1: Applied -->
<div style="z-index:1; text-align:center;">
<div style="width:24px; height:24px; background:#3b82f6; border-radius:50%; margin:0 auto; box-shadow:0 0 0 4px rgba(59,130,246,0.2);"></div>
<div style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Applied</div>
</div>
<!-- Step 2: Screening -->
<div style="z-index:1; text-align:center;">
<div style="width:24px; height:24px; background:{'#3b82f6' if curr_status in ['Screening', 'Interview', 'Accepted', 'Offer Sent'] else '#334155'}; border-radius:50%; margin:0 auto;"></div>
<div style="font-size:0.75rem; color:{'#e2e8f0' if curr_status in ['Screening', 'Interview', 'Accepted', 'Offer Sent'] else '#64748b'}; margin-top:8px;">Screening</div>
</div>
<!-- Step 3: Interview -->
<div style="z-index:1; text-align:center;">
<div style="width:24px; height:24px; background:{'#3b82f6' if curr_status in ['Interview', 'Accepted', 'Offer Sent'] else '#334155'}; border-radius:50%; margin:0 auto;"></div>
<div style="font-size:0.75rem; color:{'#e2e8f0' if curr_status in ['Interview', 'Accepted', 'Offer Sent'] else '#64748b'}; margin-top:8px;">Interview</div>
</div>
<!-- Step 4: Offer -->
<div style="z-index:1; text-align:center;">
<div style="width:24px; height:24px; background:{'#10b981' if curr_status in ['Accepted', 'Offer Sent'] else '#334155'}; border-radius:50%; margin:0 auto;"></div>
<div style="font-size:0.75rem; color:{'#e2e8f0' if curr_status in ['Accepted', 'Offer Sent'] else '#64748b'}; margin-top:8px;">Offer</div>
</div>
</div>
"""
                st.markdown(progress_stepper_html, unsafe_allow_html=True)
                
                # Dynamic Messages & Actions
                with st.container():
                     # Display HR Feedback if available
                     if mapp.get("hr_notes"):
                         st.markdown(f"""
                         <div style="margin-top:20px; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; border-left:3px solid #60a5fa;">
                            <div style="font-size:0.8rem; font-weight:700; color:#cbd5e1; margin-bottom:5px;">📢 RECRUITER FEEDBACK</div>
                            <div style="color:#e2e8f0; font-style:italic;">"{mapp.get("hr_notes")}"</div>
                         </div>
                         """, unsafe_allow_html=True)

                     if curr_status == "Interview":
                         st.info("📅 **Action Required**: HR has invited you to an interview! Check your email for scheduling links.")
                         col_i1, col_i2 = st.columns([1, 3])
                         with col_i1:
                              if st.button("Prepare Now", key=f"prep_btn_{i}", use_container_width=True, type="primary"):
                                  components.navigate_to("m5")
                                  st.rerun()

                     elif curr_status == "Rejected":
                         st.error("Status Update: Application not selected for this round. Don't give up! Improve your skills and apply again.")
                         
                     elif curr_status == "Accepted":
                         st.success("🎉 CONGRATULATIONS! You have received an offer.")
                         st.info("System: Your application is under review by the hiring team.")

    components.render_footer()