import streamlit as st
import components
import pandas as pd
import random
import time
import textwrap

def app():
    import plotly.express as px
    import plotly.graph_objects as go
    st.markdown("""
    <style>
    /* Global HR Theme Override */
    .stApp {
        background: #0f172a !important; /* Slate 900 */
    }
    
    /* Modern Card Style */
    .hr-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .hr-card:hover {
        border-color: rgba(99, 102, 241, 0.5); /* Indigo 500 */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* Metric Cards - Sleek Glass */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-lbl {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-top: 5px;
    }
    .metric-trend {
        font-size: 0.8rem;
        margin-top: 10px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .trend-up { color: #10b981; }
    .trend-down { color: #ef4444; }

    /* Kanban Columns */
    .kanban-col-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px;
        background: rgba(255,255,255,0.03);
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .kanban-col-body {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 0 0 8px 8px;
        padding: 10px;
        min-height: 400px;
        border: 1px solid rgba(255,255,255,0.02);
    }
    
    /* Candidate Card */
    .cand-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        cursor: pointer;
        position: relative;
    }
    .cand-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
    }
    .cand-role { font-size: 0.75rem; color: #94a3b8; margin-bottom: 8px; }
    .cand-name { font-weight: 600; color: #f1f5f9; font-size: 0.95rem; }
    .score-pill {
        font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 700;
        display: inline-block; margin-right: 5px;
    }

    /* Modal / Detail View Styles */
    .detail-header {
        background: linear-gradient(90deg, #1e1b4b, #312e81);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #4338ca;
    }
    
    .evaluation-section {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    
    /* CUSTOM TABS LOOK-ALIKE (Styled Radio) */
    /* Hide the radio circle */
    div[data-testid="stRadio"] > label > div:first-child {
        display: none;
    }
    /* Style the labels to look like tabs */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0px;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 10px 15px !important;
        margin: 0 !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        transition: color 0.2s, border-bottom 0.2s;
        border-bottom: 2px solid transparent !important;
    }
    /* Selected State */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #6366f1 !important; /* brand color underline */
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        color: #cbd5e1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    components.render_navbar()

    # ---------------------------------------------------------
    # STATE MANAGEMENT
    # ---------------------------------------------------------
    import uuid

    if "hr_active_tab_index" not in st.session_state:
        st.session_state["hr_active_tab_index"] = 0
    
    if "selected_candidate_id" not in st.session_state:
        st.session_state["selected_candidate_id"] = None
        
    if "selected_app_id" not in st.session_state:
        st.session_state["selected_app_id"] = None

    # Load Data
    apps = st.session_state.get("applications", [])
    jobs = st.session_state.get("jobs", [])
    
    # Ensure items have IDs
    for a in apps:
        if "_id" not in a:
            a["_id"] = str(uuid.uuid4())

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.markdown(textwrap.dedent("""\
            <div style="padding-top:20px;">
                <div style="font-size:0.8rem; font-weight:700; color:#818cf8; letter-spacing:1px; margin-bottom:5px;">ENTERPRISE EDITION</div>
                <h1 style="margin:0; font-size:2.8rem; font-weight:900; background: -webkit-linear-gradient(0deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">HR Command Center</h1>
                <p style="color:#64748b; font-size:1.1rem;">Orchestrate your entire recruitment lifecycle with AI-enhanced decision making.</p>
            </div>
        """), unsafe_allow_html=True)
    with c_head2:
        st.markdown(textwrap.dedent(f"""\
            <div style="text-align:right; padding-top:25px;">
                <div style="background:#1e293b; padding:10px 20px; border-radius:12px; border:1px solid #334155; display:inline-block;">
                    <div style="font-size:0.75rem; color:#94a3b8;">ACTIVE JOB POSTINGS</div>
                    <div style="font-size:1.5rem; font-weight:700; color:white;">{len(jobs)}</div>
                </div>
                 <div style="margin-top:10px; font-size:0.8rem; color:#10b981;">● System Operational</div>
            </div>
        """), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # METRICS ROW
    # ---------------------------------------------------------
    # Calculate Metrics
    total_apps = len(apps)
    active_cand = len([a for a in apps if a.get("status") not in ["Rejected", "Offer Sent", "Accepted"]])
    accepted_cand = len([a for a in apps if a.get("status") == "Accepted"])
    rejected_cand = len([a for a in apps if a.get("status") == "Rejected"])
    
    # Calculate quality trend
    scores = [a.get("score", 0) for a in apps] if apps else []
    avg_score = sum(scores) // len(scores) if scores else 0
    
    st.markdown(textwrap.dedent(f"""\
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-val">{total_apps}</div>
                <div class="metric-lbl">Total Candidates</div>
                <div class="metric-trend trend-up">▲ 12% vs last week</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{active_cand}</div>
                <div class="metric-lbl">Active Pipeline</div>
                <div class="metric-trend trend-up">● Healthy Flow</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{accepted_cand}</div>
                <div class="metric-lbl">Offers/Accepted</div>
                <div class="metric-trend" style="color:{'#10b981' if accepted_cand>0 else '#94a3b8'};">● Selection Ratio: {int(accepted_cand/total_apps*100) if total_apps else 0}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{avg_score}%</div>
                <div class="metric-lbl">Avg Quality Score</div>
                <div class="metric-trend trend-up">▲ 5% vs benchmark</div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    tab_options = ["📊 Live Pipeline", "👥 Ecosystem", "📈 Analytics", "👔 Requisitions", "⚙️ Settings"]
    
    selected_tab_name = st.radio(
        "Navigation", 
        tab_options, 
        index=st.session_state["hr_active_tab_index"], 
        horizontal=True, 
        key="hr_nav_radio",
        label_visibility="collapsed"
    )
    
    new_index = tab_options.index(selected_tab_name)
    if new_index != st.session_state["hr_active_tab_index"]:
        st.session_state["hr_active_tab_index"] = new_index
        st.rerun()

    active_idx = st.session_state["hr_active_tab_index"]


    # ========================== TAB 1: DASHBOARD & PIPELINE ==========================
    if active_idx == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🚀 Live Pipeline")
        k_cols = st.columns(5)
        stages = [
            ("Pending", "#94a3b8", "clock"),
            ("Screening", "#f59e0b", "search"),
            ("Interview", "#3b82f6", "video"),
            ("Accepted", "#10b981", "check-circle"),
            ("Rejected", "#ef4444", "x-circle")
        ]
        
        # Organize data
        pipeline = {s[0]: [] for s in stages}
        for a in apps:
            stat = a.get("status", "Pending")
            if stat in pipeline:
                pipeline[stat].append(a)
        
        for i, (stage, color, icon) in enumerate(stages):
            with k_cols[i]:
                # Header
                st.markdown(textwrap.dedent(f"""\
                    <div class="kanban-col-header" style="border-color:{color}; color:{color};">
                        <span>{stage}</span>
                        <span style="background:{color}20; padding:2px 8px; border-radius:10px; font-size:0.8rem;">{len(pipeline[stage])}</span>
                    </div>
                """), unsafe_allow_html=True)
                
                # Column Body
                with st.container(height=500, border=True):
                    cand_list = pipeline[stage]
                    if not cand_list:
                        st.markdown(f"<div style='text-align:center; color:#475569; padding-top:20px; font-size:0.9rem;'>No candidates</div>", unsafe_allow_html=True)
                    
                    for idx, cand in enumerate(cand_list):
                        s = cand.get("score", 0)
                        hr_s = cand.get("hr_score", 0)
                        
                        s_col = "#10b981" if s > 80 else "#f59e0b" if s > 60 else "#ef4444"
                        
                        hr_score_disp = ""
                        if hr_s > 0:
                             hr_score_disp = f'<span class="score-pill" style="background:#6366f120; color:#818cf8;">HR: {hr_s}</span>'
                        
                        with st.container():
                            st.markdown(f"""
<div class="cand-card" style="border-left: 3px solid {s_col};">
<div class="cand-name">{cand.get('applicant', 'Unknown')}</div>
<div class="cand-role">{cand.get('job_role', 'N/A')}</div>
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<span class="score-pill" style="background:{s_col}20; color:{s_col};">AI: {s}%</span>
{hr_score_disp}
</div>
</div>
<div style="font-size:0.7rem; color:#64748b; margin-top:5px;">{cand.get('applied_at', 'Recently')}</div>
</div>
""", unsafe_allow_html=True)
                            
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("Manage", key=f"dd_{stage}_{idx}", use_container_width=True):
                                
                                    st.session_state["selected_app_id"] = cand.get("_id")
                            
                                    st.session_state["hr_active_tab_index"] = 1 # Switch to Ecosystem tab
                                    # Safe state reset
                                    if "hr_nav_radio" in st.session_state:
                                        del st.session_state["hr_nav_radio"]
                                    st.rerun()
                            with b2:
                                if stage == "Pending":
                                    if st.button("Screen", key=f"adv_{stage}_{idx}", use_container_width=True, type="primary"):
                                        cand["status"] = "Screening"
                                        components.save_progress()
                                        st.rerun()
                                elif stage == "Screening":
                                    if st.button("Interview", key=f"int_{stage}_{idx}", use_container_width=True, type="primary"):
                                        cand["status"] = "Interview"
                                        components.save_progress()
                                        st.rerun()

    # ========================== TAB 2: CANDIDATE ECOSYSTEM (ADVANCED) ==========================
    elif active_idx == 1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.markdown("### 📂 Talent Ecosystem")
            st.caption("AI-Powered Candidate Search & Evaluation Engine")
        with t_col2:
            st.button("📥 Export CSV", use_container_width=True)

        # B. Smart Filters
        with st.expander("🔍 Advanced Filters & Search", expanded=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                search_q = st.text_input("Keywords", placeholder="Name, Skill, or Tag...")
            with f_col2:
                filter_role = st.selectbox("Job Role", ["All"] + [j["role"] for j in jobs])
            with f_col3:
                filter_status = st.selectbox("Pipeline Stage", ["All", "Pending", "Screening", "Interview", "Accepted", "Rejected"])
            with f_col4:
                filter_score = st.slider("Min AI Score", 0, 100, 0)
        
        # Filter Logic
        filtered_apps = apps
        if search_q:
            filtered_apps = [a for a in filtered_apps if search_q.lower() in str(a).lower()]
        if filter_role != "All":
            filtered_apps = [a for a in filtered_apps if a.get("job_role") == filter_role]
        if filter_status != "All":
            filtered_apps = [a for a in filtered_apps if a.get("status") == filter_status]
        filtered_apps = [a for a in filtered_apps if a.get("score", 0) >= filter_score]
        
        # C. Master Data View
        if filtered_apps:
            df_display = pd.DataFrame([{
                "ID": a.get("applicant"), 
                "Candidate": a["applicant"],
                "Role Applied": a["job_role"],
                "AI Score": a["score"],
                "HR Score": a.get("hr_score", 0),
                "Exp (Yrs)": random.randint(1, 15),
                "Top Skills": ", ".join(random.sample(["Python", "React", "AWS", "SQL", "Docker", "Go"], 3)), # Mock
                "Status": a["status"]
            } for a in filtered_apps])
            
            selection = st.dataframe(
                df_display,
                use_container_width=True,
                column_config={
                    "AI Score": st.column_config.ProgressColumn("Fit Score", format="%d%%", min_value=0, max_value=100),
                    "HR Score": st.column_config.NumberColumn("HR Eval", min_value=0, max_value=100, format="%d"),
                    "Candidate": st.column_config.TextColumn("Candidate Name", width="medium"),
                    "Status": st.column_config.SelectboxColumn("Stage", options=["Pending", "Screening", "Interview", "Accepted", "Rejected"], width="small"),
                },
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            if selection.selection and selection.selection.rows:
                selected_row_idx = selection.selection.rows[0]
                if selected_row_idx < len(filtered_apps):
                    selected_app_obj = filtered_apps[selected_row_idx]
                    
                    # Update pointer
                    ptr = selected_app_obj.get("_id")
                    if st.session_state.get("selected_app_id") != ptr:
                        st.session_state["selected_app_id"] = ptr
                        st.rerun()

        else:
            st.info("No candidates match the current filters.")

        # ---------------------------------------------------------
        # 2. DETAIL VIEW (CONDITIONAL - APPEARS BELOW)
        # ---------------------------------------------------------
        candidate = None
        ptr = st.session_state.get("selected_app_id")
        if ptr:
             # Find by UUID
             candidate = next((a for a in apps if a.get("_id") == ptr), None)
             
        if candidate:
            st.markdown("---")
            
            # --- SCORING & VERDICT LOGIC ---
            ai_score = candidate.get('score', 0)
            hr_score = candidate.get('hr_score', 0)
            
            # Get Job Target Score
            target_job = next((j for j in jobs if j["role"] == candidate.get("job_role")), None)
            min_req = target_job["min_score"] if target_job else 70
            
            # Verdict Logic
            is_passed = False
            verdict_text = "PENDING REVIEW"
            verdict_color = "#94a3b8" 
            
            if hr_score > 0:
                # If HR has scored, use that as confirmation
                if hr_score >= min_req:
                     is_passed = True
                     verdict_text = "PASSED"
                     verdict_color = "#10b981"
                else:
                     verdict_text = "DID NOT PASS"
                     verdict_color = "#ef4444" 
            else:
                # Auto-Verdict based on AI Score vs Min Req
                if ai_score >= min_req:
                    verdict_text = "QUALIFIED"
                    verdict_color = "#10b981"
                elif ai_score >= (min_req - 10):
                    verdict_text = "POTENTIAL"
                    verdict_color = "#f59e0b" 
                else:
                    verdict_text = "NOT QUALIFIED"
                    verdict_color = "#ef4444" 
            
            st.markdown(f"### 👤 Analysis: {candidate['applicant']}")
            
            # --- SCORECARD BANNER ---
            st.markdown(textwrap.dedent(f"""
<div style="display:flex; gap:15px; align-items:stretch; margin-bottom:20px;">
<!-- AI Score Card -->
<div style="flex:1; background:#1e293b; border:1px solid #334155; border-radius:12px; padding:15px; text-align:center;">
<div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">AI Score</div>
<div style="font-size:2.2rem; font-weight:900; color:{'#10b981' if ai_score >= min_req else '#f59e0b'};">{ai_score}%</div>
<div style="font-size:0.7rem; color:#64748b;">Candidate Fin.</div>
</div>

<!-- Target Score Card -->
<div style="flex:1; background:#0f172a; border:1px solid #334155; border-radius:12px; padding:15px; text-align:center; position:relative;">
<div style="position:absolute; top:5px; right:10px; font-size:1.2rem;">🎯</div>
<div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">Target</div>
<div style="font-size:2.2rem; font-weight:900; color:#e2e8f0;">{min_req}%</div>
<div style="font-size:0.7rem; color:#64748b;">Min Required</div>
</div>
                
<!-- HR Score Card -->
<div style="flex:1; background:#1e293b; border:1px solid #334155; border-radius:12px; padding:15px; text-align:center;">
<div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">HR Eval</div>
<div style="font-size:2.2rem; font-weight:900; color:{'#10b981' if hr_score >= min_req else '#64748b'};">{hr_score if hr_score > 0 else '--'}</div>
<div style="font-size:0.7rem; color:#64748b;">Manual Input</div>
</div>
                
<!-- Verdict Card -->
<div style="flex:1.5; background:{verdict_color}15; border:2px solid {verdict_color}; border-radius:12px; padding:15px; display:flex; align-items:center; justify-content:center; flex-direction:column;">
<div style="font-size:0.8rem; color:{verdict_color}; font-weight:bold; letter-spacing:2px; text-transform:uppercase;">Verdict</div>
<div style="font-size:1.8rem; font-weight:900; color:{verdict_color}; text-shadow:0 0 15px {verdict_color}30;">{verdict_text}</div>
</div>
            </div>
            """), unsafe_allow_html=True)
            
            # --- TOP PROFILE HEADER ---
            with st.container():
                h_c1, h_c2 = st.columns([1, 4])
                with h_c1:
                    # Avatar
                    st.markdown(f"""
                    <div style="width:120px; height:120px; background:linear-gradient(135deg, #6366f1, #8b5cf6); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:3rem; font-weight:bold; color:white; margin:0 auto; box-shadow:0 10px 20px rgba(99,102,241,0.3);">
                    {candidate['applicant'][0]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                with h_c2:
                    st.markdown(f"## {candidate['applicant']}")
                    st.markdown(f"**{candidate['job_role']}**")
                    st.markdown("📧 candidate@example.com | 📞 +1 (555) 019-2834")
                    st.markdown(f"📍 {random.choice(['New York, USA', 'London, UK', 'Remote', 'Berlin, DE'])}")
                    
                    # Status Badge
                    st.caption(f"Current Status: **{candidate['status']}**")

                    # Badges (Moved here)
                    st.markdown(f"""
                     <div style="display:flex; gap:8px; margin-top:10px;">
                        <span style="background:#334155; padding:5px 10px; border-radius:20px; font-size:0.8rem;">🚀 Fast Track</span>
                        <span style="background:#334155; padding:5px 10px; border-radius:20px; font-size:0.8rem;">⭐ Top School</span>
                        <span style="background:#334155; padding:5px 10px; border-radius:20px; font-size:0.8rem;">💼 5+ Yrs Exp</span>
                     </div>
                     """, unsafe_allow_html=True)

            # --- TABS FOR DEEP DIVE ---
            d_tab1, d_tab2, d_tab3, d_tab4 = st.tabs(["🧠 Skills Radar", "📋 Resume", "🤖 AI Persona", "⚡ Actions & Score"])
            
            # 1. SKILLS RADAR (Advanced Visuals)
            with d_tab1:
                r_c1, r_c2 = st.columns([2, 1])
                with r_c1:
                    # Mock Radar Data
                    categories = ['Coding', 'System Design', 'Communication', 'Experience', 'Culture Fit']
                    r_values = [
                        ai_score if ai_score < 100 else 95, 
                        random.randint(60, 90), 
                        random.randint(70, 95), 
                        random.randint(50, 85), 
                        random.randint(80, 100)
                    ]
                    
                    fig_radar = go.Figure(data=go.Scatterpolar(
                      r=r_values,
                      theta=categories,
                      fill='toself',
                      name=candidate['applicant'],
                      line_color='#818cf8',
                      fillcolor='rgba(99, 102, 241, 0.3)'
                    ))

                    fig_radar.update_layout(
                      polar=dict(
                        radialaxis=dict(
                          visible=True,
                          range=[0, 100],
                          tickfont=dict(color='gray'),
                          gridcolor='#334155'
                        ),
                        bgcolor='rgba(0,0,0,0)'
                      ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='white'),
                      margin=dict(l=40, r=40, t=20, b=20),
                      showlegend=False
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                with r_c2:
                    st.markdown("#### 🔍 Insights")
                    st.markdown(f"""
                    - **Strongest Area**: {categories[r_values.index(max(r_values))]} ({max(r_values)}%)
                    - **Development Need**: {categories[r_values.index(min(r_values))]} ({min(r_values)}%)
                    """)
                    st.info("💡 Candidate is in the top 15% for Technical Skills.")
                    
                    st.markdown("#### ✅ Validated Skills")
                    for m in ["Python", "Docker", "SQL"]:
                         st.markdown(f"- {m}")

            # 2. RESUME VIEW
            with d_tab2:
                st.info("📄 Resume content extracted from PDF.")
                st.text_area("Raw Resume Text", value=f"Mock resume text for {candidate['applicant']}...\n\nExperience:\n- Senior Developer at Tech Co (2020-Present)\n- Junior Dev at Startup (2018-2020)\n\nSkills:\nPython, JS, React...", height=300)

            # 3. AI PERSONA
            with d_tab3:
                st.markdown("#### 🧬 Behavioral Insight (Generated by AI)")
                persona_traits = {
                    "Openness": 88,
                    "Conscientiousness": 92,
                    "Extraversion": 65,
                    "Agreeableness": 75,
                    "Neuroticism": 40
                }
                
                p_cols = st.columns(5)
                for k, v in persona_traits.items():
                    with p_cols[list(persona_traits.keys()).index(k)]:
                        st.markdown(f"<div style='text-align:center; font-weight:bold; font-size:0.8rem;'>{k}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; font-size:1.2rem; color:#818cf8;'>{v}%</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**Summary:** This candidate demonstrates high **Owner Mindset**. They are likely to be self-driven and meticulous (High Conscientiousness).")

            # 4. ACTIONS & SCORING
            with d_tab4:
                st.markdown("#### ⚡ Communication & Evaluation Studio")
                
                # Container for better layout
                with st.container():
                     # 1. HR Score Section
                     st.markdown("##### 📝 1. Manual Assessment")
                     st.caption("Adjust the slider to set your manual evaluation score. This updates the Verdict instantly.")
                     
                     current_hr = candidate.get("hr_score", 0)
                     # Using a unique key prevents stuck state
                     new_hr_score = st.slider("HR Score (0-100)", 0, 100, current_hr, key=f"hr_sl_dyn_{candidate['_id']}")
                     
                     # Immediate State Update Logic
                     if new_hr_score != current_hr:
                         candidate["hr_score"] = new_hr_score
                         components.save_progress() # Save to disk
                         st.rerun() # Refresh UI to show new score/verdict

                     st.markdown("---")

                     # 2. Action Selection Section
                     st.markdown("##### 🚀 2. Pipeline Decision")
                     
                     action_type = st.radio(
                         "Select Action", 
                         ["Invite to Interview", "Send Rejection", "Send Offer"], 
                         horizontal=True,
                         label_visibility="collapsed"
                     )

                     # Pre-fill content
                     email_subject = ""
                     email_body = ""
                     header_color = "#3b82f6"
                     
                     if action_type == "Invite to Interview":
                         email_subject = f"Interview Invitation: {candidate['job_role']}"
                         email_body = f"Hi {candidate['applicant'].split()[0]},\n\nWe were impressed by your profile and would like to invite you for an interview.\n\nPlease let us know your availability.\n\nBest,\nRecruiting Team"
                         header_color = "#3b82f6"
                     elif action_type == "Send Rejection":
                         email_subject = f"Application Update: {candidate['job_role']}"
                         email_body = f"Hi {candidate['applicant'].split()[0]},\n\nThank you for your interest. Unfortunately, we have decided to proceed with other candidates at this time.\n\nBest,\nRecruiting Team"
                         header_color = "#ef4444" 
                     else:
                         email_subject = f"Offer Letter: {candidate['job_role']}"
                         email_body = f"Hi {candidate['applicant'].split()[0]},\n\nWe are thrilled to offer you the position!\n\nBest,\nRecruiting Team"
                         header_color = "#10b981" 
                     
                     # Preview Card
                     st.markdown(f"""
                     <div style="border-left:4px solid {header_color}; background:#1e293b; padding:15px; margin-top:10px; border-radius:4px;">
                        <div style="font-weight:bold; color:white;">📧 Preview: {email_subject}</div>
                        <div style="color:#94a3b8; font-size:0.9rem; margin-top:5px; white-space: pre-wrap;">{email_body}</div>
                     </div>
                     """, unsafe_allow_html=True)
                     
                     st.markdown("<br>", unsafe_allow_html=True)
                     
                     if st.button(f"Confirm & Send {action_type.split()[-1]}", key=f"confirm_send_{candidate['_id']}_{action_type}", type="primary", use_container_width=True):
                         # Status Mapping
                         new_status = ""
                         if "Invite" in action_type: new_status = "Interview"
                         elif "Rejection" in action_type: new_status = "Rejected"
                         else: new_status = "Accepted"
                         
                         candidate["status"] = new_status
                         candidate["hr_notes"] = f"Action: {action_type}. Status: {new_status}. Score: {new_hr_score}"
                         
                         # CRITICAL: Save and Force Rerun
                         components.save_progress()
                         
                         st.toast(f"Status Updated to {new_status}!", icon="✅")
                         time.sleep(0.5)
                         st.rerun()

    # ========================== TAB 3: REAL ANALYTICS ==========================
    elif active_idx == 2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### � Recruitment Performance Analytics")
        
        # Aggregation Logic
        total_apps = len(apps)
        rejected = len([a for a in apps if a['status'] == 'Rejected'])
        interview = len([a for a in apps if a['status'] == 'Interview'])
        accepted = len([a for a in apps if a['status'] == 'Accepted'])
        pending = len([a for a in apps if a['status'] in ['Pending', 'Screening']])
        
        # 1. KPI Row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Candidates", total_apps)
        k2.metric("Interviews Active", interview, delta="high priority")
        k3.metric("Offers Accepted", accepted, delta_color="normal")
        k4.metric("Rejections", rejected, delta_color="inverse")
        
        st.markdown("---")
        
        # 2. Charts Row
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🌪️ Pipeline Funnel")
            funnel_data = dict(
                number=[total_apps, pending + interview + accepted, interview + accepted, accepted],
                stage=["Applied", "Screening", "Interview", "Hired"]
            )
            fig_funnel = px.funnel(funnel_data, x='number', y='stage')
            fig_funnel.update_traces(marker_color=["#6366f1", "#8b5cf6", "#ec4899", "#10b981"])
            fig_funnel.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_funnel, use_container_width=True)
            
        with c2:
            st.markdown("##### 🥧 Status Distribution")
            pie_df = pd.DataFrame({
                "Status": ["Pending", "Interview", "Rejected", "Accepted"],
                "Count": [pending, interview, rejected, accepted]
            })
            # Filter out zeros for cleaner chart
            pie_df = pie_df[pie_df["Count"] > 0]
            
            fig_pie = px.pie(pie_df, values="Count", names="Status", hole=0.5, 
                             color="Status",
                             color_discrete_map={
                                 "Pending": "#94a3b8",
                                 "Interview": "#f59e0b",
                                 "Rejected": "#ef4444", 
                                 "Accepted": "#10b981"
                             })
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### 🏆 Top Skill Demand")
        # Mock Bar Chart
        sk_df = pd.DataFrame({
            "Skill": ["Python", "React", "AWS", "SQL", "Docker", "Kubernetes"],
            "Count": [85, 72, 65, 50, 45, 40]
        })
        fig_bar = px.bar(sk_df, x="Skill", y="Count", color="Count", color_continuous_scale="Viridis")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_bar, use_container_width=True)

    # ========================== TAB 4: JOB MANAGEMENT ==========================
    elif active_idx == 3:
        st.markdown("<br>", unsafe_allow_html=True)
        j_c1, j_c2 = st.columns([1, 2])
        
        with j_c1:
            st.markdown(textwrap.dedent("""\
                <div style="background:#1e293b; padding:25px; border-radius:16px; border:1px solid #334155;">
                    <h3 style="margin-top:0; color:white;">📝 Create Requisition</h3>
                    <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:20px;">Launch a new role to the career portal.</p>
                </div>
            """), unsafe_allow_html=True)
            
            with st.form("job_create_form"):
                 role = st.text_input("Role Title")
                 dept = st.text_input("Department", value="Engineering")
                 loc = st.text_input("Location", value="Remote")
                 min_s = st.slider("Min Match Score", 50, 95, 75)
                 desc = st.text_area("Description Preview", height=100)
                 
                 if st.form_submit_button("🚀 Publish Role", use_container_width=True, type="primary"):
                     new_job = {
                         "id": f"JOB-{random.randint(5000,9999)}",
                         "role": role,
                         "company": f"{dept} • {loc}",
                         "location": loc,
                         "min_score": min_s
                     }
                     st.session_state.setdefault("jobs", []).append(new_job)
                     st.success("Requisition Created!")
                     st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with j_c2:
            st.markdown("### Active Requisitions")
            if not jobs:
                st.info("No active jobs found.")
            else:
                for job in jobs:
                    st.markdown(textwrap.dedent(f"""\
                        <div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-size:1.2rem; font-weight:700; color:white;">{job['role']}</div>
                                <div style="color:#94a3b8; font-size:0.9rem;">{job['company']}</div>
                                <div style="margin-top:8px;">
                                    <span style="background:#3b82f620; color:#60a5fa; padding:2px 8px; border-radius:4px; font-size:0.75rem;">{job['location']}</span>
                                    <span style="background:#f472b620; color:#f472b6; padding:2px 8px; border-radius:4px; font-size:0.75rem; margin-left:8px;">Min Score: {job['min_score']}%</span>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-weight:700; font-size:1.5rem; color:#10b981;">{random.randint(2, 15)}</div>
                                <div style="font-size:0.7rem; text-transform:uppercase; color:#64748b;">Applicants</div>
                            </div>
                        </div>
                    """), unsafe_allow_html=True)
    
    # ========================== TAB 5: SETTINGS ==========================
    elif active_idx == 4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ⚙️ System Configuration")
        
        s1, s2 = st.columns(2)
        with s1:
            st.toggle("Enable AI Auto-Screening", value=True)
            st.toggle("Send Auto-Rejections (<50% match)", value=False)
            st.toggle("Anonymize Candidate Profiles (Bias Reduction)", value=False)
        with s2:
            st.selectbox("Integration Mode", ["Greenhouse", "Lever", "Workday", "Standalone (Active)"])
            st.slider("Global Latency Threshold (ms)", 100, 2000, 450)

    components.render_footer()
