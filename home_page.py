import streamlit as st
from components import navigate_to, load_lottiefile, load_lottieurl
import components
import textwrap

def app():
    import textwrap
    # -------------------------
    # HOME PAGE LOGIC
    # -------------------------
    st.markdown("""
    <style>
        :root {
            --card-bg: #020617;
            --card-border: 1px solid #1f2937;
            --card-shadow: 0 10px 40px rgba(15,23,42,0.6);
            --text-color: #e5e7eb;
            --muted-color: #9ca3af;
            --accent-color: #3b82f6;
            --success-color: #10b981;
            --error-color: #ef4444;
            --footer-height: 72px;
        }
        
        /* Global Horizontal Scroll Fix */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        /* Full Width Hero Section */
        .hero-section {
            margin-top: 50px;
            height: 600px;
            position: relative;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            left: 0;
            background: #020617;
            background-image: radial-gradient(at 80% 50%, #1e3a8a 0px, transparent 50%),
                              radial-gradient(at 0% 0%, #0f172a 0px, transparent 50%);
            color: white;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            z-index: 0;
            box-sizing: border-box;
        }
        
        .hero-content-wrapper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .hero-title {
            font-size: 4.5rem; font-weight: 900;
            background: linear-gradient(to right, #ffffff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            text-shadow: 0 10px 30px rgba(0,0,0,0.3);
            line-height: 1.1;
        }
        .hero-subtitle {
            font-size: 1.3rem; 
            color: white; 
            opacity: 0.9; 
            margin-bottom: 30px;
        }
        
        /* Stats Bar */
        .stats-bar {
            display: flex;
            justify-content: space-around;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 30px;
            margin: 40px 0;
            backdrop-filter: blur(5px);
        }
        .stat-item { text-align: center; }
        .stat-num { font-size: 2.5rem; font-weight: 800; color: #3b82f6; }
        .stat-desc { font-size: 0.9rem; color: var(--muted-color); text-transform: uppercase; }
        
        /* Uniform Cards */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .uniform-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 25px;
            height: 100%;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s;
        }
        .uniform-card:hover { transform: translateY(-5px); border-color: #3b82f6; }
        
        /* Why Choose Us Grid */
        .benefits-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin-top: 20px;
        }
        .benefit-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 50px 30px;
            min-height: 320px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            transition: all 0.3s ease;
        }
        .benefit-card:hover {
            transform: scale(1.05);
            background: rgba(255, 255, 255, 0.05);
            border-color: #3b82f6;
        }
        
        /* Progress Timeline */
        .progress-container {
            display: flex;
            justify-content: space-between;
            position: relative;
            margin: 60px 0;
        }
        .progress-line {
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 4px;
            background: #1e293b;
            z-index: 0;
            transform: translateY(-50%);
        }
        .progress-step {
            width: 40px; height: 40px;
            background: #0f172a;
            border: 2px solid #3b82f6;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            z-index: 1;
            color: #3b82f6;
            font-weight: bold;
        }
        
        /* Scrollable Carousel */
        .carousel-wrapper {
            overflow: hidden;
            white-space: nowrap;
            padding: 20px 0;
            position: relative;
        }
        .carousel-track {
            display: inline-block;
            animation: scroll 20s linear infinite;
        }
        .course-card {
            display: inline-block;
            min-width: 200px;
            background: linear-gradient(135deg, #1e3a8a, #172554);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-right: 20px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        
        /* Testimonials */
        .testimonial-card {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.05);
            position: relative;
        }
        .testimonial-card::before {
            content: "“";
            font-size: 4rem;
            color: #3b82f6;
            opacity: 0.2;
            position: absolute;
            top: 10px;
            left: 10px;
            line-height: 0;
        }
        
        /* Floating Journey Cards */
        .journey-card {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            height: 100%;
            border: 1px solid rgba(255,255,255,0.08);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .journey-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 100%;
            background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, transparent 100%);
            z-index: 0;
        }
        
        .journey-card:hover {
            transform: translateY(-10px);
            background: rgba(30, 41, 59, 0.8);
            border-color: #3b82f6;
            box-shadow: 0 20px 50px rgba(59, 130, 246, 0.15);
        }
        
        .journey-step {
            position: absolute;
            top: 10px;
            right: 20px;
            font-size: 4rem;
            font-weight: 900;
            color: rgba(255, 255, 255, 0.02);
            line-height: 1;
            z-index: 0;
        }
        
        .journey-icon-box {
            width: 70px;
            height: 70px;
            background: rgba(59, 130, 246, 0.05); /* Very subtle blue tint */
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.4s ease;
            position: relative;
            z-index: 1;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .journey-card:hover .journey-icon-box {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
        }
        
        .journey-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
        }
        
        .journey-desc {
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.5;
            position: relative;
            z-index: 1;
            margin-bottom: 15px;
        }
        
        /* STREAMLIT BUTTON OVERRIDES */
        div.stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
        }
        div.stButton > button:hover {
            background-color: #2563eb !important;
            color: white !important;
        }

        /* AI SCANNER ANIMATION */
        .scanner-box {
            position: relative;
            width: 260px;
            height: 340px;
            margin: 40px auto;
            perspective: 1000px;
        }
        .resume-paper {
            width: 100%;
            height: 100%;
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
            transform: rotateY(-12deg) rotateX(5deg);
            animation: float-paper 6s ease-in-out infinite;
        }
        .resume-header {
            display: flex; align-items: center; margin-bottom: 20px;
        }
        .resume-avatar {
            width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 50%; margin-right: 15px;
        }
        .resume-line {
            height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-bottom: 12px;
        }
        .resume-content { padding: 25px; }
        
        .scan-laser {
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent, #3b82f6, transparent);
            box-shadow: 0 0 20px #3b82f6, 0 0 10px #60a5fa;
            z-index: 10;
            animation: scanning 3s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            opacity: 0.8;
        }
        
        .skill-badge {
            position: absolute;
            padding: 6px 14px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34d399;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            backdrop-filter: blur(4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 20;
            pointer-events: none;
        }
        
        @keyframes float-paper {
            0%, 100% { transform: rotateY(-12deg) rotateX(5deg) translateY(0); }
            50% { transform: rotateY(-12deg) rotateX(5deg) translateY(-20px); }
        }
        @keyframes scanning {
            0% { top: -10%; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { top: 110%; opacity: 0; }
        }
        @keyframes pop-skill {
            0% { transform: scale(0) translateZ(0); opacity: 0; }
            20% { transform: scale(1.1) translateZ(20px); opacity: 1; }
            80% { transform: scale(1) translateZ(20px); opacity: 1; }
            100% { transform: scale(0) translateZ(0); opacity: 0; }
        }

        /* NEW POWERFUL TOOLS SECTION STYLES */
        .section-header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }
        .section-header h2 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .section-header p {
            color: #94a3b8;
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .tool-card {
            position: relative;
            border-radius: 24px;
            padding: 1px; /* The border width */
            transition: all 0.4s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .tool-card-inner {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(2, 6, 23, 0.95));
            backdrop-filter: blur(20px);
            border-radius: 23px;
            padding: 40px 30px;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }
        
        /* Specific Styles for Resume Builder Card */
        .tool-card.resume-card {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.4), rgba(59, 130, 246, 0.4));
            box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.1), 0 20px 40px -10px rgba(168, 85, 247, 0.2);
        }
        .tool-card.resume-card:hover {
            box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.3), 0 30px 60px -15px rgba(168, 85, 247, 0.4);
            transform: translateY(-5px);
        }
        
        /* Specific Styles for ATS Checker Card */
        .tool-card.ats-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.4), rgba(14, 165, 233, 0.4));
            box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.1), 0 20px 40px -10px rgba(16, 185, 129, 0.2);
        }
        .tool-card.ats-card:hover {
            box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.3), 0 30px 60px -15px rgba(16, 185, 129, 0.4);
            transform: translateY(-5px);
        }

        .tool-icon-circle {
            width: 80px; height: 80px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 2.5rem;
            margin-bottom: 25px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: inset 0 0 20px rgba(255,255,255,0.02);
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
        }
        
        /* Glow behind icon */
        .tool-icon-circle::after {
            content: '';
            position: absolute;
            width: 100%; height: 100%;
            border-radius: 50%;
            filter: blur(20px);
            opacity: 0.4;
            z-index: -1;
        }
        
        .resume-card .tool-icon-circle::after { background: #a855f7; }
        .ats-card .tool-icon-circle::after { background: #10b981; }

        .tool-card:hover .tool-icon-circle {
            transform: scale(1.1) rotate(5deg);
            background: rgba(255,255,255,0.08);
        }
        
        .tool-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 15px;
        }
        
        .tool-desc {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 0;
        }
        
        /* Decorative ambient blobs inside card */
        .ambient-blob {
            position: absolute;
            width: 150px; height: 150px;
            border-radius: 50%;
            filter: blur(50px);
            opacity: 0.15;
            z-index: 0;
            pointer-events: none;
        }
        .top-blob { top: -50px; right: -50px; background: white; }
        .bottom-blob { bottom: -50px; left: -50px; }

        /* ROLE ACCESS SECTION STYLES */
        .role-wrapper {
            margin-top: 30px;
        }
        .role-card {
            background: linear-gradient(145deg, #0f172a, #020617);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 0;
            overflow: hidden;
            height: 100%;
            transition: all 0.4s ease;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }
        .role-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        
        .role-header-bg {
            height: 140px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        .role-header-bg::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-size: cover;
            background-position: center;
            opacity: 0.6;
            transition: transform 6s ease;
        }
        .role-card:hover .role-header-bg::before {
            transform: scale(1.1);
        }
        
        /* Student Theme */
        .role-card.student { border-bottom: 4px solid #3b82f6; }
        .role-card.student .role-header-bg { background: linear-gradient(45deg, #1e3a8a, #3b82f6); }
        .role-card.student .role-header-bg::before { 
            background-image: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.2) 0%, transparent 60%); 
        }
        
        /* Recruiter Theme */
        .role-card.recruiter { border-bottom: 4px solid #ec4899; }
        .role-card.recruiter .role-header-bg { background: linear-gradient(45deg, #831843, #ec4899); }
        .role-card.recruiter .role-header-bg::before {
             background-image: radial-gradient(circle at 70% 50%, rgba(255,255,255,0.2) 0%, transparent 60%); 
        }

        .role-content {
            padding: 0 30px 30px 30px;
            position: relative;
            z-index: 2;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        
        .role-icon-box {
            width: 64px; height: 64px;
            border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            font-size: 2rem;
            margin-top: -32px;
            margin-bottom: 20px;
            background: #0f172a;
            border: 4px solid #020617;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            position: relative;
            z-index: 10;
        }
        
        .role-title {
            font-size: 1.6rem;
            font-weight: 800;
            color: white;
            margin-bottom: 5px;
        }
        .role-subtitle {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 15px;
            display: block;
        }
        .student .role-subtitle { color: #60a5fa; }
        .recruiter .role-subtitle { color: #f472b6; }
        
        .role-desc {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 25px;
            margin-top: auto; 
        }
        .feature-item {
            display: flex;
            align-items: center;
            font-size: 0.85rem;
            color: #cbd5e1;
            background: rgba(255,255,255,0.03);
            padding: 8px 12px;
            border-radius: 8px;
        }
        .f-icon { margin-right: 8px; font-weight: bold; }
        .student .f-icon { color: #3b82f6; }
        .recruiter .f-icon { color: #ec4899; }
    </style>
    """, unsafe_allow_html=True)

    # 1. NAVBAR
    components.render_navbar()

    # 3. HERO CONTENT
    st.markdown('<div style="margin-top: -650px; position: relative; z-index: 10; padding: 0 20px;">', unsafe_allow_html=True)
    
    col_hero_left, col_hero_right = st.columns([1.2, 1])
    
    with col_hero_left:
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
        st.markdown(textwrap.dedent("""\
            <div class="hero-title">Unlock Your<br>Career Potential</div>
            <div class="hero-subtitle">AI-powered skill gap analysis, resume optimization, and personalized learning paths.</div>
        """), unsafe_allow_html=True)
        
        # Buttons
        st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
        b1, b2 = st.columns([1, 1])
        with b1:
            st.button("🎓 Student Access", type="primary", use_container_width=True, on_click=navigate_to, args=("Student Dashboard",))
        with b2:
            st.button("👥 Recruiter Portal", type="secondary", use_container_width=True, on_click=navigate_to, args=("HR Dashboard",))

    with col_hero_right:
        # AI SCANNER ANIMATION
        st.markdown(textwrap.dedent("""
            <div class="scanner-box">
                <!-- Floating Resume Paper -->
                <div class="resume-paper">
                    <div class="scan-laser"></div>
                    <div class="resume-content">
                        <div class="resume-header">
                            <div class="resume-avatar"></div>
                            <div style="flex:1;">
                                <div class="resume-line" style="width:60%;"></div>
                                <div class="resume-line" style="width:40%; height:6px;"></div>
                            </div>
                        </div>
                        <div class="resume-line" style="width:100%; margin-top:30px;"></div>
                        <div class="resume-line" style="width:90%;"></div>
                        <div class="resume-line" style="width:95%;"></div>
                        <div class="resume-line" style="width:80%; margin-top:20px;"></div>
                        <div class="resume-line" style="width:85%;"></div>
                    </div>
                </div>
                
<!-- Floating Detected Skills -->
<div class="skill-badge" style="top: 20px; right: -30px; animation: pop-skill 4s infinite 0s;">JavaScript</div>
<div class="skill-badge" style="bottom: 80px; left: -40px; animation: pop-skill 4s infinite 1.5s;">Leadership</div>
<div class="skill-badge" style="top: 150px; right: -50px; animation: pop-skill 4s infinite 2.5s;">98% Match</div>
<div class="skill-badge" style="bottom: 20px; right: 0px; background:rgba(59,130,246,0.15); color:#60a5fa; border-color:rgba(59,130,246,0.4); animation: pop-skill 4s infinite 3.5s;">Optimized</div>
</div>
"""), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 4. ANIMATED STATS BAR
    st.markdown(textwrap.dedent("""\
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-num">12k+</div>
                <div class="stat-desc">Users Trained</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">89%</div>
                <div class="stat-desc">Success Rate</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">98%</div>
                <div class="stat-desc">AI Accuracy</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">50k+</div>
                <div class="stat-desc">Resumes Fixed</div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # 5. HOW IT WORKS
    st.markdown("<div id='how-it-works'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin-top:60px;'>⚡ How It Works</h3>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""\
        <div class="progress-container">
            <div class="progress-line"></div>
            <div class="progress-step">1</div>
            <div class="progress-step">2</div>
            <div class="progress-step">3</div>
            <div class="progress-step">4</div>
        </div>
        <div style="display:flex; justify-content:space-between; text-align:center; font-size:0.9rem; color:var(--muted-color); margin-top:-40px; padding: 0 10px;">
            <div><strong>Upload</strong><br>Resume & JD</div>
            <div><strong>Extract</strong><br>AI Parsing</div>
            <div><strong>Analyze</strong><br>Gap Detection</div>
            <div><strong>Report</strong><br>Get Hired</div>
        </div>
    """), unsafe_allow_html=True)

    # 6. NAVIGATION GRID
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Start Your Journey")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(textwrap.dedent("""\
            <div class="journey-card">
                <div class="journey-step">01</div>
                <div class="journey-icon-box"><div style="font-size:2rem;">📂</div></div>
                <div class="journey-title">Ingestion</div>
                <div class="journey-desc">Upload your resume and job description to get started.</div>
            </div>
        """), unsafe_allow_html=True)
        st.button("Start Ingestion ➡️", key="nav_btn_1", use_container_width=True, on_click=navigate_to, args=("Milestone 1: Data Ingestion",))

    with col2:
        st.markdown(textwrap.dedent("""\
            <div class="journey-card">
                <div class="journey-step">02</div>
                <div class="journey-icon-box"><div style="font-size:2rem;">🧠</div></div>
                <div class="journey-title">Extraction</div>
                <div class="journey-desc">AI identifies your key skills and experience automatically.</div>
            </div>
        """), unsafe_allow_html=True)
        st.button("Go to Extraction ➡️", key="nav_btn_2", use_container_width=True, on_click=navigate_to, args=("Milestone 2: Skill Extraction",))

    with col3:
        st.markdown(textwrap.dedent("""\
            <div class="journey-card">
                <div class="journey-step">03</div>
                <div class="journey-icon-box"><div style="font-size:2rem;">📊</div></div>
                <div class="journey-title">Analysis</div>
                <div class="journey-desc">Visualize skill gaps and market demand in real-time.</div>
            </div>
        """), unsafe_allow_html=True)
        st.button("View Analysis ➡️", key="nav_btn_3", use_container_width=True, on_click=navigate_to, args=("Milestone 3: Gap Analysis",))

    with col4:
        st.markdown(textwrap.dedent("""\
            <div class="journey-card">
                <div class="journey-step">04</div>
                <div class="journey-icon-box"><div style="font-size:2rem;">📈</div></div>
                <div class="journey-title">Report</div>
                <div class="journey-desc">Get your personalized roadmap and optimized resume.</div>
            </div>
        """), unsafe_allow_html=True)
        st.button("Get Report ➡️", key="nav_btn_4", use_container_width=True, on_click=navigate_to, args=("Milestone 4: Dashboard & Report",))

    # 6.5 TOOLS SECTION
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Section Header
    st.markdown("""
        <div class="section-header">
            <h2>🚀 Powerful Career Superpowers</h2>
            <p>Everything you need to land your dream job, powered by advanced AI agencies.</p>
        </div>
    """, unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns(2)
        
    with t_col1:
        st.markdown(textwrap.dedent("""\
<div class="tool-card resume-card">
<div class="tool-card-inner">
<div class="ambient-blob top-blob" style="background: #a855f7;"></div>
<div class="ambient-blob bottom-blob" style="background: #3b82f6;"></div>

<div class="tool-icon-circle">📝</div>
<div class="tool-title">AI Resume Builder</div>
<div class="tool-desc">
Construct a flawless, ATS-proof resume in minutes. leverages our
fine-tuned LLMs to rewrite your content for maximum impact.
</div>
</div>
            </div>
        """), unsafe_allow_html=True)
        # Spacer
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        st.button("Build Your Resume 🚀", key="home_tool_btn_1", use_container_width=True, type="primary", on_click=navigate_to, args=("Resume Builder",))

    with t_col2:
        st.markdown(textwrap.dedent("""\
<div class="tool-card ats-card">
<div class="tool-card-inner">
<div class="ambient-blob top-blob" style="background: #10b981;"></div>
<div class="ambient-blob bottom-blob" style="background: #0ea5e9;"></div>

<div class="tool-icon-circle">🎯</div>
<div class="tool-title">ATS Score Checker</div>
<div class="tool-desc">
Don't guess—know. Run your resume against our enterprise-grade
parser to see exactly what recruiters see.
</div>
</div>
            </div>
        """), unsafe_allow_html=True)
        # Spacer
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        st.button("Check ATS Score 📊", key="home_tool_btn_2", use_container_width=True, type="secondary", on_click=navigate_to, args=("ATS Report",))

    # 6.6 DASHBOARD PORTALS SECTION
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="section-header">
            <h2>🚪 Choose Your Portal</h2>
            <p>Access specialized tools tailored to your role in the hiring ecosystem.</p>
        </div>
    """, unsafe_allow_html=True)
    
    d_col1, d_col2 = st.columns(2)
    
    with d_col1:
        st.markdown(textwrap.dedent("""\
            <div class="role-card student">
                 <div class="role-header-bg"></div>
                 <div class="role-content">
                     <div class="role-icon-box">🎓</div>
                     <span class="role-subtitle">For Job Seekers</span>
                     <div class="role-title">Student Workstation</div>
                     <p class="role-desc">
                        Your command center for career acceleration. Track applications, 
                        visualize skill gaps, and access exclusive learning resources to 
                        stand out from the crowd.
                     </p>
                     
<div class="feature-grid">
                        <div class="feature-item"><span class="f-icon">✓</span> Skill Gaps</div>
                        <div class="feature-item"><span class="f-icon">✓</span> Job Board</div>
                        <div class="feature-item"><span class="f-icon">✓</span> Resume AI</div>
                        <div class="feature-item"><span class="f-icon">✓</span> Badges</div>
                     </div>
                 </div>
            </div>
        """), unsafe_allow_html=True)
        # Spacer
        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
        st.button("Enter Student Portal 🚀", key="home_dash_btn_1", use_container_width=True, type="primary", on_click=navigate_to, args=("Student Dashboard",))
        
    with d_col2:
        st.markdown(textwrap.dedent("""\
            <div class="role-card recruiter">
                 <div class="role-header-bg"></div>
                 <div class="role-content">
                     <div class="role-icon-box">👥</div>
                     <span class="role-subtitle">For Hiring Teams</span>
                     <div class="role-title">Recruiter Hub</div>
                     <p class="role-desc">
                        Streamline your hiring pipeline with AI-driven candidate screening. 
                        Post jobs, manage applications, and identify top talent instantly 
                        with semantic matching.
                     </p>
                     
<div class="feature-grid">
<div class="feature-item"><span class="f-icon">✓</span> Post Jobs</div>
<div class="feature-item"><span class="f-icon">✓</span> AI Screen</div>
<div class="feature-item"><span class="f-icon">✓</span> Pipeline</div>
<div class="feature-item"><span class="f-icon">✓</span> Analytics</div>
</div>
                 </div>
            </div>
        """), unsafe_allow_html=True)
         # Spacer
        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
        st.button("Access HR Portal 🔐", key="home_dash_btn_2", use_container_width=True, type="secondary", on_click=navigate_to, args=("HR Dashboard",))

    # 7. VIZ
    st.markdown("<br>", unsafe_allow_html=True)
    import plotly.express as px
    import pandas as pd
    import numpy as np

    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        st.subheader("🌐 Global Skill Demand Heatmap")
        df_map = pd.DataFrame({
            "Country": ["USA", "India", "Germany", "UK", "Canada", "Australia"],
            "Demand": [95, 90, 85, 80, 75, 70],
            "Code": ["USA", "IND", "DEU", "GBR", "CAN", "AUS"]
        })
        fig_map = px.choropleth(df_map, locations="Code", color="Demand", hover_name="Country",
                                color_continuous_scale="Viridis", projection="natural earth")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_map, use_container_width=True)
    with col_viz2:
        st.subheader("🔮 3D Skill Cluster Analysis")
        df_3d = pd.DataFrame({
            "Hard Skills": np.random.rand(100),
            "Soft Skills": np.random.rand(100),
            "Experience": np.random.rand(100),
            "Category": np.random.choice(["Tech", "Management", "Design"], 100)
        })
        fig_3d = px.scatter_3d(df_3d, x='Hard Skills', y='Soft Skills', z='Experience', color='Category', opacity=0.7)
        fig_3d.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig_3d, use_container_width=True)

    # 8. SCROLLABLE CAROUSEL
    st.subheader("📚 Recommended Learning Paths")
    st.markdown("""
    <div class="carousel-wrapper">
        <div class="carousel-track">
            <div class="course-card">🐍 Python Advanced</div>
            <div class="course-card">📊 Power BI Master</div>
            <div class="course-card">☁️ AWS Certified</div>
            <div class="course-card">🎨 UI/UX Design</div>
            <div class="course-card">🤖 Machine Learning</div>
            <div class="course-card">📈 Agile PM</div>
            <div class="course-card">🔐 Cybersecurity</div>
            <div class="course-card">📱 Flutter Dev</div>
            <div class="course-card">🐍 Python Advanced</div>
            <div class="course-card">📊 Power BI Master</div>
            <div class="course-card">☁️ AWS Certified</div>
            <div class="course-card">🎨 UI/UX Design</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 9. WHY CHOOSE US
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 💎 Why Choose SkillGapAI?")
    st.markdown(textwrap.dedent("""\
        <div class="benefits-grid">
            <div class="benefit-card">
                <div style="font-size:2.5rem; margin-bottom:15px;">🚀</div>
                <h3 style="margin-bottom:10px;">ATS Optimized</h3>
                <p style="color:var(--muted-color);">Ensure your resume passes automated tracking systems with our proven optimization algorithms.</p>
            </div>
            <div class="benefit-card">
                <div style="font-size:2.5rem; margin-bottom:15px;">🧠</div>
                <h3 style="margin-bottom:10px;">Deep Learning</h3>
                <p style="color:var(--muted-color);">Powered by state-of-the-art BERT and spaCy models for true semantic understanding.</p>
            </div>
            <div class="benefit-card">
                <div style="font-size:2.5rem; margin-bottom:15px;">🎯</div>
                <h3 style="margin-bottom:10px;">Actionable Insights</h3>
                <p style="color:var(--muted-color);">Don't just see the gaps—get specific course recommendations to close them effectively.</p>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # 10. CONTINUE
    st.markdown("<br>", unsafe_allow_html=True)
    c_cont1, c_cont2, c_cont3 = st.columns([1, 2, 1])
    with c_cont2:
        st.button("🚀 Continue to Data Ingestion (Milestone 1)", type="primary", use_container_width=True, key="continue_btn_main_2", on_click=navigate_to, args=("Milestone 1: Data Ingestion",))

    # 11. RESULTS
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("⚡ Real Results")
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.markdown(textwrap.dedent("""
            <div style="background:rgba(239, 68, 68, 0.1); border:1px solid #ef4444; padding:20px; border-radius:12px;">
                <h4 style="color:#ef4444; margin:0;">Before Optimization ❌</h4>
                <h1 style="margin:10px 0;">43/100</h1>
                <p>Generic keywords, poor formatting, low ATS score.</p>
            </div>
        """), unsafe_allow_html=True)
    with c_res2:
        st.markdown(textwrap.dedent("""
            <div style="background:rgba(34, 197, 94, 0.1); border:1px solid #22c55e; padding:20px; border-radius:12px;">
                <h4 style="color:#22c55e; margin:0;">After Optimization ✅</h4>
                <h1 style="margin:10px 0;">92/100</h1>
                <p>Targeted skills, semantic matching, high impact.</p>
            </div>
        """), unsafe_allow_html=True)

    # 12. DID YOU KNOW?
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); padding: 30px; border-radius: 15px; color: white; text-align: center;">
            <h3 style="margin:0;">💡 Did You Know?</h3>
            <p style="font-size: 1.1rem; margin-top: 10px;">75% of resumes are rejected by ATS before they even reach a human recruiter. SkillGapAI ensures you're in the top 25%.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 13. TESTIMONIALS
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("🗣️ What Our Users Say")
    st.markdown(textwrap.dedent("""\
        <div class="card-grid">
            <div class="uniform-card">
                <div style="font-size:2rem; color:#3b82f6;">❝</div>
                <p style="flex-grow:1; font-style:italic; margin:10px 0;">"Landed my dream job at Google! The gap analysis was spot on."</p>
                <div><strong>Balu</strong><br><span style="font-size:0.8rem; color:gray;">Data Scientist</span></div>
            </div>
            <div class="uniform-card">
                <div style="font-size:2rem; color:#3b82f6;">❝</div>
                <p style="flex-grow:1; font-style:italic; margin:10px 0;">"The AI suggestions helped me rewrite my resume in minutes."</p>
                <div><strong>Karthik</strong><br><span style="font-size:0.8rem; color:gray;">DevOps Engineer</span></div>
            </div>
            <div class="uniform-card">
                <div style="font-size:2rem; color:#3b82f6;">❝</div>
                <p style="flex-grow:1; font-style:italic; margin:10px 0;">"Incredible tool. Highly recommended for anyone job hunting."</p>
                <div><strong>Karthi</strong><br><span style="font-size:0.8rem; color:gray;">Product Manager</span></div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # 14. FAQ
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ❓ Frequently Asked Questions")
    with st.expander("How does the AI analysis work?"):
        st.write("We use advanced Natural Language Processing (NLP) models to parse your text, extract entities (skills, experience), and compare them semantically using vector embeddings.")
    with st.expander("Is my data secure?"):
        st.write("Absolutely. Your documents are processed in-memory for the duration of your session and are not permanently stored on our servers.")
    with st.expander("Can I upload multiple resumes?"):
        st.write("Currently, the system is designed to analyze one resume against one job description at a time.")

    # 15. FOOTER
    components.render_footer()
