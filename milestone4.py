import streamlit as st
import uuid
import math
import textwrap

from datetime import datetime
import components as ui_components

try:
    from milestone2 import SKILL_CATEGORIES, get_skill_category
except ImportError:
    # Fallback if M2 not found
    SKILL_CATEGORIES = {
        "Languages": ["python", "java", "c++", "javascript", "html", "css", "sql", "bash", "r", "go", "ruby", "php", "swift", "kotlin"],
    }
    def get_skill_category(skill): return "General"

def create_full_report_pdf(stats, jd_details, missing_kws, roadmap_weeks, project_ideas=[], soft_skills=[]):
    """
    Generates a premium, magazine-style Full Intelligence Report PDF.
    Includes: Cover Page, Visual Executive Summary, Deep Dive Roadmap, and Strategic Recommendations.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import io
    import datetime

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    story = []

    # --- BRAND COLORS ---
    c_primary = colors.HexColor("#4338ca")  
    c_accent = colors.HexColor("#ec4899")   
    c_dark = colors.HexColor("#1e293b")     
    c_light = colors.HexColor("#f8fafc")    
    c_success = colors.HexColor("#10b981")  

    s_title = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=32, leading=38, textColor=c_primary, alignment=TA_CENTER)
    s_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=14, leading=18, textColor=colors.gray, alignment=TA_CENTER)
    s_header = ParagraphStyle('Header', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=18, textColor=c_dark, spaceBefore=20, spaceAfter=10)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=c_dark)
    
    # --- PAGE 1: COVER PAGE ---
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("SKILL GAP &<br/>INTELLIGENCE REPORT", s_title))
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="60%", thickness=2, color=c_accent, spaceAfter=20))
    story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}", s_subtitle))
    story.append(Spacer(1, 3*inch))
    
    # Executive Metadata Box on Cover
    meta_data = [
        ["ASSESSMENT TARGET", "Full Stack / Cloud Profile"],
        ["CURRENT MATCH SCORE", f"{stats['overall']}%"],
        ["KEY GAP AREAS", f"{len(missing_kws)} identified"]
    ]
    t_cover = Table(meta_data, colWidths=[2.5*inch, 2.5*inch])
    t_cover.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.gray),
        ('TEXTCOLOR', (1,0), (1,-1), c_dark),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('SIZE', (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(t_cover)
    story.append(PageBreak())

    # --- PAGE 2: EXECUTIVE BLUEPRINT ---
    story.append(Paragraph("Executive Blueprint", s_header))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=15))
    
    # 1. Score Cards as text blocks with background
    score = stats['overall']
    grade = "A" if score > 90 else "B" if score > 75 else "C"
    
    t_cards = Table([
        ["OVERALL SCORE", "ASSESSMENT GRADE", "CRITICAL GAPS"],
        [f"{score}/100", grade, str(len(missing_kws))]
    ], colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), c_primary),
        ('BACKGROUND', (1,0), (1,-1), c_accent),
        ('BACKGROUND', (2,0), (2,-1), c_dark),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
        ('SIZE', (0,1), (-1,-1), 22),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,1), (-1,-1), 15),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 25))

    # 2. Strategic Analysis Text
    story.append(Paragraph("Strategic Analysis", ParagraphStyle('H3', parent=s_header, fontSize=14)))
    analysis_text = f"Based on the job description analysis, your profile demonstrates strong alignment in core areas. However, <b>{len(missing_kws)} specific high-value keywords</b> were identified as missing or under-represented. Closing these gaps is projected to increase your interview probability by approximately <b>40%</b>."
    story.append(Paragraph(analysis_text, s_body))
    story.append(Spacer(1, 20))

    # 3. Missing Skills List
    story.append(Paragraph("High-Priority Missing Skills", ParagraphStyle('H3', parent=s_header, fontSize=14)))
    
    # Group into rows of 4 for grid
    skill_rows = []
    chunk = []
    for sk in missing_kws[:12]: 
        chunk.append(sk)
        if len(chunk) == 4:
            skill_rows.append(chunk)
            chunk = []
    if chunk: skill_rows.append(chunk + ['']*(4-len(chunk)))
    
    if skill_rows:
        t_skills = Table(skill_rows, colWidths=[1.7*inch]*4)
        t_skills.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,-1), c_dark),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('SIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.white),
        ]))
        story.append(t_skills)
    else:
        story.append(Paragraph("No critical gaps found. Excellent coverage!", s_body))

    story.append(PageBreak())

    # --- PAGE 3: ACTION ROADMAP ---
    story.append(Paragraph("4-Week Acceleration Roadmap", s_header))
    story.append(Paragraph("A structured timeline to mastery.", s_body))
    story.append(Spacer(1, 15))

    for week in roadmap_weeks:
        # Header for Week
        story.append(Table(
            [[week['title'], week['desc'].upper()]], 
            colWidths=[1.5*inch, 5.5*inch],
            style=TableStyle([
                ('BACKGROUND', (0,0), (0,0), c_primary),
                ('TEXTCOLOR', (0,0), (0,0), colors.white),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (0,0), 'CENTER'),
                ('BACKGROUND', (1,0), (1,0), colors.HexColor("#e0e7ff")),
                ('TEXTCOLOR', (1,0), (1,0), c_primary),
                ('ALIGN', (1,0), (1,0), 'LEFT'),
                ('LEFTPADDING', (1,0), (1,0), 10),
            ])
        ))
        
        # Content
        focus_items = ", ".join(week['focus']) if week['focus'] else "Consolidation & Review"
        content_text = f"<b>Focus Areas:</b> {focus_items}<br/><br/><i>Recommended Actions:</i><br/>• Complete crash course on highlighted topics.<br/>• Build a mini-project integrating these skills."
        
        story.append(Table(
            [['', Paragraph(content_text, s_body)]],
            colWidths=[0.2*inch, 6.8*inch],
            style=TableStyle([
                ('LINEBELOW', (1,0), (1,0), 0.5, colors.lightgrey),
                ('BOTTOMPADDING', (1,0), (1,0), 10),
                ('TOPPADDING', (1,0), (1,0), 10),
            ])
        ))
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 20))
    story.append(PageBreak())

    # --- PAGE 4: STRATEGIC GROWTH ---
    story.append(Paragraph("Strategic Growth Plan", s_header))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=15))

    # --- SECTION: SALARY INSIGHTS ---
    story.append(Paragraph("Market Value Projection", ParagraphStyle('H3', parent=s_header, fontSize=14)))
    
    current_est = 85000 + (stats['overall'] * 500)
    potential_est = current_est * 1.35
    
    t_salary = Table([
        ["CURRENT ESTIMATE", "POTENTIAL (After Upskilling)"],
        [f"${current_est:,.0f} / yr", f"${potential_est:,.0f} / yr"]
    ], colWidths=[3.5*inch, 3.5*inch])
    
    t_salary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f1f5f9")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#ecfdf5")),
        ('TEXTCOLOR', (0,1), (0,1), colors.HexColor("#64748b")),
        ('TEXTCOLOR', (1,1), (1,1), c_success),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('SIZE', (0,1), (-1,-1), 16),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('BOX', (0,0), (-1,-1), 1, colors.white),
    ]))
    story.append(t_salary)
    story.append(Paragraph(f"Closing your skill gaps represents a +35% growth opportunity in the current market.", ParagraphStyle('caption', parent=s_body, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 20))

    # --- SECTION: CAPSTONE PROJECTS ---
    if project_ideas:
        story.append(Paragraph("Recommended Capstone Projects", ParagraphStyle('H3', parent=s_header, fontSize=14)))
        for p in project_ideas:
            # Create a nice box for each project
            p_title = Paragraph(f"<b>{p['title']}</b>", ParagraphStyle('PTitle', parent=s_body, fontSize=11, textColor=c_primary))
            p_desc = Paragraph(p['desc'], s_body)
            p_tags = Paragraph(f"<i>Tags: {', '.join(p['tags'])}</i>", ParagraphStyle('PTags', parent=s_body, fontSize=9, textColor=colors.gray))
            
            story.append(Table(
                [[p_title], [p_desc], [p_tags]],
                colWidths=[7*inch],
                style=TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
                    ('LEFTPADDING', (0,0), (-1,-1), 12),
                    ('RIGHTPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ])
            ))
            story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 15))

    # --- SECTION: SOFT SKILLS ---
    if soft_skills:
        story.append(Paragraph("Soft Skills Development", ParagraphStyle('H3', parent=s_header, fontSize=14)))
        
        soft_rows = [["Focus Area", "Actionable Step"]]
        for s in soft_skills:
            soft_rows.append([s['title'], s['desc']])
            
        t_soft = Table(soft_rows, colWidths=[2.5*inch, 4.5*inch])
        t_soft.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_dark),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ]))
        story.append(t_soft)
        story.append(Spacer(1, 20))

    # --- NEW SECTION: CERTIFICATION PATHS ---
    story.append(Paragraph("Recommended Certifications", s_header))
    story.append(Paragraph("Based on your gap analysis, prioritizing these certifications will yield high ROI.", s_body))
    story.append(Spacer(1, 10))
    
    # Logic to suggest certs
    certs = []
    gaps_str = " ".join([str(k).lower() for k in missing_kws])
    if "aws" in gaps_str or "cloud" in gaps_str: certs.append(["AWS Certified Solutions Architect", "High Priority"])
    else: certs.append(["AWS Certified Solutions Architect", "General Recommendation"])
    
    if "azure" in gaps_str: certs.append(["Microsoft Certified: Azure Fundamentals", "Medium Priority"])
    if "python" in gaps_str or "data" in gaps_str: certs.append(["Google Data Analytics Professional", "High Priority"])
    if "kubernetes" in gaps_str or "docker" in gaps_str: certs.append(["CKA: Certified Kubernetes Administrator", "High Priority"])
    if "react" in gaps_str: certs.append(["Meta Front-End Developer Professional", "Medium Priority"])
    
    # Fill if empty
    if len(certs) < 3:
        certs.append(["General Agile / Scrum Certification", "Soft Skill"])
        certs.append(["System Design Interview Prep", "Architecture"])
    
    t_certs = Table([["Certification Name", "Priority"]] + certs, colWidths=[5*inch, 1.5*inch])
    t_certs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), c_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('TEXTCOLOR', (1,1), (1,-1), c_success),
        ('FONTNAME', (1,1), (1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_certs)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_ats_resume(original_resume_text, missing_skills, job_title="Target Role"):
    """
    Generates a simple text-based ATS optimized resume by appending a 'Targeted Skills' section.
    """
    optimization_section = f"""
    
    --------------------------------------------------------------------------------
    ATS OPTIMIZATION REPORT & SUGGESTED ADDITIONS
    --------------------------------------------------------------------------------
    Target Role: {job_title}
    Date: {datetime.now().strftime('%Y-%m-%d')}
    
    [SUGGESTED SKILLS SECTION TO ADD]
    To improve your match score, consider incorporating the following relevant skills 
    into your "Skills" or "Summary" section, provided you possess them:
    
    {', '.join(missing_skills)}
    
    [OPTIMIZED SUMMARY SUGGESTION]
    "Professional aiming for {job_title} with a strong foundation in current technologies. 
    Passionate about leveraging skills in {', '.join(missing_skills[:3])} to drive results."
    
    --------------------------------------------------------------------------------
    ORIGINAL RESUME CONTENT
    --------------------------------------------------------------------------------
    """
    return optimization_section + original_resume_text

def app():
    ui_components.render_navbar()
    st.markdown(ui_components.get_page_css(), unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""\
        <style>
        /* M4 Specific Styles */
        .m4-header {
            background: linear-gradient(120deg, #4F46E5, #06B6D4);
            padding: 30px;
            border-radius: 16px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
            text-align: center;
        }
        
        /* Metric Cards */
        .metric-card {
            background: var(--card-bg);
            border: var(--card-border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: var(--card-shadow);
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-val { font-size: 2.2rem; font-weight: 800; color: var(--text-color); }
        .metric-lbl { font-size: 0.85rem; color: var(--muted-color); text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }
        
        /* Roadmap Items */
        .roadmap-item {
            background: rgba(255,255,255,0.03);
            border-left: 4px solid #3B82F6;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
        }
        .roadmap-week { font-size: 0.8rem; color: #3B82F6; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
        .roadmap-title { font-size: 1.1rem; font-weight: 600; color: var(--text-color); }
        .roadmap-desc { font-size: 0.95rem; color: var(--text-color); margin-bottom: 5px; }
        .roadmap-desc { font-size: 0.9rem; color: var(--muted-color); }
        
        /* ATS Box */
        .ats-box {
            background: rgba(245, 158, 11, 0.05);
            border: 1px dashed var(--warning-color);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }
        
        /* Rec Card (Old Style preserved) */
        .rec-card {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid var(--success-color);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .rec-title {
            font-weight: bold;
            color: var(--success-color);
        }

        /* Dashboard Banner (Old Style preserved) */
        .dashboard-banner {
            background: var(--card-bg);
            border-radius: 999px;
            padding: 10px 18px;
            border: var(--card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
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
            background-color: rgba(79, 70, 229, 0.1);
            color: #818cf8;
        }

        /* Primary = LIGHT BLUE (Indigo Style for Contact/Main Actions) */
        .stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {
            background: linear-gradient(90deg, #818CF8 0%, #6366F1 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3) !important;
        }
        .stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.5) !important;
        }

        /* Secondary = GREEN (For Feedback) */
        .stButton button[kind="secondary"], .stDownloadButton button[kind="secondary"] {
            background: linear-gradient(90deg, #10B981 0%, #059669 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3) !important;
        }
        .stButton button[kind="secondary"]:hover, .stDownloadButton button[kind="secondary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.5) !important;
            color: white !important;
        }
        </style>
        """), unsafe_allow_html=True
    )
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    ui_components.render_stepper(current_step=4)

    logo_svg = '<svg width="35" height="35" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon"><defs><linearGradient id="grad4" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#22D3EE" /><stop offset="100%" stop-color="#3B82F6" /></linearGradient><filter id="glow4" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><rect x="10" y="10" width="44" height="44" rx="12" stroke="url(#grad4)" stroke-width="4" fill="none"/><path d="M24 36L30 36L28 46L40 28L34 28L36 18L24 36Z" fill="white" filter="url(#glow4)"/><circle cx="32" cy="8" r="3" fill="#22D3EE"/><circle cx="32" cy="56" r="3" fill="#3B82F6"/><circle cx="8" cy="32" r="3" fill="#22D3EE"/><circle cx="56" cy="32" r="3" fill="#3B82F6"/></svg>'

    st.markdown(
        f"""
        <div class="hero-section" style="background: linear-gradient(120deg, #4F46E5, #3730A3); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); position: relative; overflow: hidden; margin-top: 20px;">
            <div class="hero-title" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px; display: flex; align-items: center; justify-content: center; gap: 15px;">
                {logo_svg}
                <div>Final Intelligence Report</div>
            </div>
            <div class="hero-sub" style="font-size: 1.1rem; opacity: 0.9; font-weight: 300;">End-to-end comparison, strategic roadmap, and ATS optimization.</div>
        </div>
        """, unsafe_allow_html=True
    )

    # Check Results
    if "m3_results" not in st.session_state:
        st.warning("⚠️ No analysis results found. Please go to **Milestone 3** and run the analysis first.")

        return
    
    # Lazy load heavy libraries now that we have data
    import charts
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    results = st.session_state["m3_results"]
    stats = results["stats"]
    jd_details = results["jd_details"]
    resume_skills = results["resume_skills"]
    jd_skills = results["jd_skills"]
    resume_text_original = st.session_state.get("resume_manual", "")
    critical_skills = results.get("critical_skills", [])
    
    # Calculate all gaps for use across tabs
    if "m4_data" in st.session_state and "all_gaps" in st.session_state["m4_data"]:
        all_gaps = st.session_state["m4_data"]["all_gaps"]
    else:
        all_gaps = [d['jd_skill'] for d in jd_details if d['category'] in ["Low Match", "Partial Match"]]


    tab_dash, tab_roadmap, tab_report = st.tabs(["📊 Executive Dashboard", "🗺️ Strategic Roadmap", "💎 Final Intelligence Report"])

    # =========================================================
    # TAB 1: EXECUTIVE DASHBOARD
    # =========================================================
    with tab_dash:
        st.markdown("---")

        # 1. Key Metrics Row
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        
        score_color = "#10B981" if stats['overall'] > 75 else "#F59E0B" if stats['overall'] > 50 else "#EF4444"
        
        with c_m1:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:{score_color}">{stats["overall"]}%</div><div class="metric-lbl">Match Score</div></div>', unsafe_allow_html=True)
        with c_m2:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{stats["matched"]}</div><div class="metric-lbl">Matched Skills</div></div>', unsafe_allow_html=True)
        with c_m3:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#F59E0B">{stats["partial"]}</div><div class="metric-lbl">Partial Matches</div></div>', unsafe_allow_html=True)
        with c_m4:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#EF4444">{stats["missing"]}</div><div class="metric-lbl">Missing Skills</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # NEW FEATURES: Interview Readiness & Salary
        c_new1, c_new2 = st.columns(2)
        with c_new1:
            readiness = min(100, stats['overall'] + 10)  
            st.markdown(textwrap.dedent(f"""\
                <div class="metric-card" style="border-left: 4px solid #8B5CF6;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #8B5CF6; margin-bottom: 5px;">🎤 Interview Readiness</div>
                    <div style="font-size: 2rem; font-weight: 800;">{readiness}%</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Based on technical skill coverage</div>
                </div>
                """), unsafe_allow_html=True
            )
        with c_new2:
            st.markdown(
                """
                <div class="metric-card" style="border-left: 4px solid #10B981;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #10B981; margin-bottom: 5px;">💰 Salary Potential</div>
                    <div style="font-size: 2rem; font-weight: 800;">$85k - $120k</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Estimated market range for this role</div>
                </div>
                """, unsafe_allow_html=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Advanced Visualizations (Radar & Sunburst)
        c_viz1, c_viz2 = st.columns([1.5, 1])
        
        with c_viz1:
            with st.container(border=True):
                st.markdown("##### 🕸️ Skill Coverage by Category")
                
                # Prepare Radar Data
                all_cats = list(SKILL_CATEGORIES.keys()) + ["General"]
                
                # Helper to count skills per category
                def count_cats(skill_list):
                    counts = {c: 0 for c in all_cats}
                    for s in skill_list:
                        cat = get_skill_category(s)
                        counts[cat] += 1
                    return counts

                r_counts = count_cats(resume_skills)
                j_counts = count_cats(jd_skills)
                
                # Normalize for Radar (Percentage of JD requirements met)
                radar_vals = []
                for cat in all_cats:
                    j_val = j_counts[cat]
                    r_val = r_counts[cat]
                    if j_val == 0:
                        radar_vals.append(100 if r_val > 0 else 0)  
                    else:
                        radar_vals.append(min(100, int((r_val / j_val) * 100)))
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=radar_vals,
                    theta=all_cats,
                    fill='toself',
                    name='Coverage %',
                    line_color='#6C3CF0'
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100]),
                    ),
                    margin=dict(l=40, r=40, t=20, b=20),
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False
                )
                st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")

        with c_viz2:
            with st.container(border=True):
                st.markdown("##### 🌞 Skill Ecosystem")
                # Sunburst of JD Skills: Inner=Category, Outer=Skill, Color=Match Status
                
                sb_data = []
                # Root
                sb_data.append({"id": "Job", "parent": "", "value": 0, "color": "#333"})
                
                # Categories
                for cat in all_cats:
                    sb_data.append({"id": cat, "parent": "Job", "value": 0, "color": "#444"})
                
                # Skills
                for d in jd_details:
                    cat = get_skill_category(d['jd_skill'])
                    color = "#10B981" if d['category'] == "High Match" else "#F59E0B" if d['category'] == "Partial Match" else "#EF4444"
                    sb_data.append({
                        "id": d['jd_skill'],
                        "parent": cat,
                        "value": 1,
                        "color": color
                    })
                
                df_sb = pd.DataFrame(sb_data)
                fig_sb = charts.get_sunburst_chart(df_sb)
                st.plotly_chart(fig_sb, use_container_width=True, key="sunburst_chart_main")

        st.markdown("<br>", unsafe_allow_html=True)

        # -------------------------------------------------------
        # NEW DASHBOARD SECTIONS
        # -------------------------------------------------------
        c_new_d1, c_new_d2 = st.columns([1, 1])
        
        with c_new_d1:
            st.markdown("##### 🚀 Market Competitiveness")
        
            percentile = min(99, int(stats['overall'] * 1.1))  
            
            fig_gauge = charts.get_percentile_gauge(percentile)
            st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_chart")
            st.caption(f"You score higher than {percentile}% of candidates applying for similar roles.")

        with c_new_d2:
            st.markdown("##### ⚡ Quick Wins")
            # Identify Partial Matches that are close to High Match
            quick_wins = [d for d in jd_details if d['category'] == "Partial Match"]
            # Sort by score descending (closest to 1.0)
            quick_wins.sort(key=lambda x: x['score'], reverse=True)
            
            if quick_wins:
                st.write("Improve these skills slightly to significantly boost your score:")
                for qw in quick_wins[:3]:
                    st.markdown(
                        f"""
                        <div style="background: rgba(245, 158, 11, 0.1); padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #F59E0B; display: flex; justify-content: space-between; align-items: center;">
                            <div><strong>{qw['jd_skill']}</strong> <span style="font-size: 0.8rem; color: #cbd5e1;">(Current: {qw['score']*100:.0f}%)</span></div>
                            <div style="color: #F59E0B; font-weight: bold;">+15% Impact</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.info("No immediate 'Quick Wins' detected. Focus on your missing skills!")

            st.markdown("##### 🔑 Keyword Impact")
            # Show top missing keywords
            missing_kws = [d['jd_skill'] for d in jd_details if d['category'] == "Low Match"]
            if missing_kws:
                st.write("Missing these keywords hurts your ATS score the most:")
                st.markdown(
                    f"""
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        {''.join([f'<span style="background: rgba(239, 68, 68, 0.15); color: #fca5a5; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; border: 1px solid rgba(239, 68, 68, 0.3);">{kw}</span>' for kw in missing_kws[:6]])}
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.success("Great job! You have all major keywords covered.")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Skill Gap Severity (Bar Chart from Old Code)
        st.markdown("##### 📉 Skill Gap Severity")
        scores = [d['score'] * 100 for d in jd_details]
        skills = [d['jd_skill'] for d in jd_details]
        
        df_scores = pd.DataFrame({"Skill": skills, "Match Score": scores})
        df_scores = df_scores.sort_values("Match Score", ascending=True)
        
        fig_bar = charts.get_bar_chart(df_scores)
        st.plotly_chart(fig_bar, use_container_width=True, key="severity_bar_chart")

        # 4. Detailed Breakdown Table
        st.markdown("##### 📋 Detailed Match Analysis")
        
        # Prepare table data
        table_rows = []
        for d in jd_details:
            is_crit = "Yes" if d['jd_skill'] in critical_skills else "No"
            table_rows.append({
                "Skill": d['jd_skill'],
                "Category": get_skill_category(d['jd_skill']),
                "Your Match": d['resume_match'],
                "Score": d['score'],
                "Status": d['category'],
                "Critical": is_crit
            })
        
        df_table = pd.DataFrame(table_rows)
        st.dataframe(
            df_table,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Match %",
                    format="%.0f%%",
                    min_value=0,
                    max_value=1,
                ),
                "Status": st.column_config.TextColumn("Status"),
            },
            use_container_width=True,
            hide_index=True
        )

    # =========================================================
    # TAB 2: STRATEGIC ROADMAP
    # =========================================================
    with tab_roadmap:
        st.markdown("### 🗺️ Your 4-Week Strategic Roadmap")
        st.write("Follow this tailored plan to bridge your skill gaps and master the target role.")
        st.markdown("---")

        if "m4_data" in st.session_state and "roadmap" in st.session_state["m4_data"]:
            weeks_data = st.session_state["m4_data"]["roadmap"]
        else:
            total_skills = len(all_gaps)
            chunk_size = math.ceil(total_skills / 3)  

            w1_skills = all_gaps[:chunk_size]
            w2_skills = all_gaps[chunk_size:chunk_size*2]
            w3_skills = all_gaps[chunk_size*2:]

            weeks_data = [
                {
                    "title": "Week 1: Foundations & Core Concepts",
                    "focus": w1_skills if w1_skills else ["Core Fundamentals"],
                    "desc": "Focus on understanding the syntax, core principles, and basic usage of these technologies. Do not rush into building complex apps yet.",
                    "tasks": ["Watch crash courses (YouTube/Udemy)", "Read official documentation", "Solve 10 basic coding problems"]
                },
                {
                    "title": "Week 2: Application & Practice",
                    "focus": w2_skills if w2_skills else ["Advanced Concepts"],
                    "desc": "Start applying what you learned. If you have no new skills this week, deepen your knowledge of Week 1 skills.",
                    "tasks": ["Build small scripts/components", "Follow a 'Code-Along' tutorial", "Debug common errors"]
                },
                {
                    "title": "Week 3: Integration & Projects",
                    "focus": w3_skills if w3_skills else ["System Integration"],
                    "desc": "Combine multiple skills. For example, connect your frontend to a backend, or analyze a dataset using multiple libraries.",
                    "tasks": ["Start a Capstone Project", "Integrate APIs", "Deploy a simple version"]
                },
                {
                    "title": "Week 4: Mastery & Interview Prep",
                    "focus": ["Interview Questions", "System Design", "Soft Skills"],
                    "desc": "Polish your projects, update your resume, and prepare for technical interviews. This is about selling your skills.",
                    "tasks": ["Mock Interviews (Pramp/Interviewing.io)", "Optimize LinkedIn Profile", "Finalize Portfolio"]
                }
            ]

        for i, week in enumerate(weeks_data):
            week_num = i + 1
            skills_str = ", ".join(week['focus'])

            # Pre-calculate the list items to avoid complex nested f-strings
            tasks_html = ''.join([f'<li>{task}</li>' for task in week['tasks']])
            
            card_html = f"""
                <div class="roadmap-item" style="border-left: 4px solid {'#3B82F6' if i%2==0 else '#8B5CF6'};">
                    <div class="roadmap-week" style="color: {'#3B82F6' if i%2==0 else '#8B5CF6'};">Week {week_num}</div>
                    <div class="roadmap-title">{week['title']}</div>
                    <div style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;"><strong>Focus:</strong> {skills_str}</div>
                    <div class="roadmap-desc">{week['desc']}</div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <ul style="margin-bottom: 0; padding-left: 20px; color: #94a3b8; font-size: 0.85rem;">
                            {tasks_html}
                        </ul>
                    </div>
                </div>
            """
            st.markdown(textwrap.dedent(card_html), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
 
        c_act1, c_act2 = st.columns(2)
        
        with c_act1:
            st.markdown('<h4 style="display:flex; align-items:center; gap:10px;">📚 <span style="background:linear-gradient(90deg, #60A5FA, #A78BFA); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:800;">Learning Playlist</span></h4>', unsafe_allow_html=True)
            
            resources_html = '<div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); padding: 20px;">'
            
            if all_gaps:
                for idx, skill in enumerate(all_gaps[:4]):
                    search_url = f"https://www.google.com/search?q={skill}+course+free"
                    icon = "🔹"
                    if idx == 0: icon = "🔥"
                    if idx == 1: icon = "⚡"
                    
                    resources_html += f"""
<div style="display:flex; align-items:center; justify-content:space-between; padding: 12px; margin-bottom:10px; background:rgba(255,255,255,0.03); border-radius:12px; border:1px solid rgba(255,255,255,0.02); transition: transform 0.2s;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="background:rgba(59,130,246,0.2); width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.1rem;">{icon}</div>
        <div>
            <div style="font-weight:700; color:#f1f5f9; font-size:1rem;">{skill}</div>
            <div style="font-size:0.75rem; color:#94a3b8;">Essential Gap</div>
        </div>
    </div>
    <a href="{search_url}" target="_blank" style="background:linear-gradient(90deg, #3b82f6, #2563eb); color:white; padding:8px 16px; border-radius:8px; font-size:0.8rem; text-decoration:none; font-weight:600; box-shadow:0 4px 6px rgba(59, 130, 246, 0.3);">Start</a>
</div>
"""
                resources_html += '<div style="text-align:center; margin-top:10px;"><a href="#" style="color:#60a5fa; font-size:0.85rem; text-decoration:none; opacity:0.8;">View Full Curriculum →</a></div>'
            else:
                resources_html += '<div style="padding:20px; text-align:center; color:#94a3b8;">🎉 No major gaps found! You are ready to build.</div>'
            
            resources_html += "</div>"
            st.markdown(resources_html, unsafe_allow_html=True)
        
        with c_act2:
            st.markdown('<h4 style="display:flex; align-items:center; gap:10px;">🛠️ <span style="background:linear-gradient(90deg, #34D399, #2DD4BF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:800;">Capstone Studio</span></h4>', unsafe_allow_html=True)
            
            if "m4_data" in st.session_state and "projects" in st.session_state["m4_data"]:
                projects = st.session_state["m4_data"]["projects"]
            else:
                # Logic for projects
                cats = set([get_skill_category(s) for s in all_gaps])
                projects = []
                
                if "Data Science" in cats:
                    projects.append({
                        "title": "Predictive Analytics Dashboard",
                        "desc": "Analyze a complex dataset to visualize trends & predict future outcomes.",
                        "tags": ["Data Viz", "ML"],
                        "color": "#F472B6" 
                    })
                elif "Frameworks" in cats or "Languages" in cats:
                    projects.append({
                        "title": "Full-Stack Task Manager",
                        "desc": "Build a scalable CRUD app with a modern frontend and robust backend.",
                        "tags": ["FullStack", "API"],
                        "color": "#34D399"
                    })
                else:
                    projects.append({
                        "title": "Skill Showcase Portfolio",
                        "desc": "A responsive personal website highlighting your resume and top projects.",
                        "tags": ["Web", "Design"],
                        "color": "#60A5FA"
                    })
                    
                projects.append({
                        "title": "Intelligent Automation Script",
                        "desc": "Python script to automate daily workflows like file sorting or email reports.",
                        "tags": ["Automation", "Scripting"],
                        "color": "#FBBF24"
                })
            
            proj_html = '<div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); padding: 20px;">'
            
            for p in projects:
                 proj_html += f"""
<div style="background:rgba(255,255,255,0.03); border-radius:12px; padding:16px; margin-bottom:12px; border-left:4px solid {p['color']}; position:relative; overflow:hidden;">
    <div style="font-weight:700; color:{p['color']}; font-size:1.1rem; margin-bottom:4px;">{p['title']}</div>
    <div style="font-size:0.9rem; color:#cbd5e1; margin-bottom:10px; line-height:1.4;">{p['desc']}</div>
    <div style="display:flex; gap:6px;">
        {''.join([f'<span style="background:{p["color"]}20; color:{p["color"]}; padding:2px 8px; border-radius:6px; font-size:0.7rem; font-weight:600;">{t}</span>' for t in p['tags']])}
    </div>
</div>
"""
            
            proj_html += "</div>"
            st.markdown(proj_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # -------------------------------------------------------
        # 3. CERTIFICATIONS & SOFT SKILLS
        # -------------------------------------------------------
        c_cert, c_soft = st.columns(2)
        
        with c_cert:
            st.markdown('<h4 style="display:flex; align-items:center; gap:10px;">🏆 <span style="background:linear-gradient(90deg, #F59E0B, #D97706); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:800;">Recommended Credentials</span></h4>', unsafe_allow_html=True)
            
            certs = [
                {"title": "AWS Cloud Practitioner", "reason": "Essential for modern backend roles.", "icon": "☁️"},
                {"title": "Google Data Analytics", "reason": "Industry standard for data roles.", "icon": "📊"},
                {"title": "Meta Front-End Dev", "reason": "Perfect for React/UI gaps.", "icon": "⚛️"}
            ]
            
            cert_html = '<div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); padding: 20px;">'
            
            for c in certs:
                cert_html += f"""
<div style="display:flex; gap:15px; background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; border:1px solid rgba(245, 158, 11, 0.15); margin-bottom:12px; align-items:center;">
    <div style="background:rgba(245, 158, 11, 0.15); min-width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">{c['icon']}</div>
    <div>
        <div style="color:#ffffff; font-weight:700; font-size:1rem; margin-bottom:2px;">{c['title']}</div>
        <div style="color:#cbd5e1; font-size:0.85rem;">{c['reason']}</div>
    </div>
</div>
"""
            cert_html += "</div>"
            st.markdown(cert_html, unsafe_allow_html=True)

        with c_soft:
            st.markdown('<h4 style="display:flex; align-items:center; gap:10px;">🤝 <span style="background:linear-gradient(90deg, #34D399, #10B981); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:800;">Soft Skills</span></h4>', unsafe_allow_html=True)
            
            actions = [
                {"title": "Technical Comm.", "desc": "Explain code to a non-tech friend.", "icon": "🗣️"},
                {"title": "Networking 5x5", "desc": "Connect with 5 recruiters in 5 days.", "icon": "🌐"},
                {"title": "Community Dev", "desc": "Join a Discord/Slack for devs.", "icon": "👥"}
            ]
            
            soft_html = '<div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); padding: 20px;">'
            
            for a in actions:
                 soft_html += f"""
<div style="display:flex; gap:15px; background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; border:1px solid rgba(52, 211, 153, 0.15); margin-bottom:12px; align-items:center;">
    <div style="background:rgba(52, 211, 153, 0.15); min-width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">{a['icon']}</div>
    <div>
        <div style="color:#ffffff; font-weight:700; font-size:1rem; margin-bottom:2px;">{a['title']}</div>
        <div style="color:#cbd5e1; font-size:0.85rem;">{a['desc']}</div>
    </div>
</div>
"""
            soft_html += "</div>"
            st.markdown(soft_html, unsafe_allow_html=True)

    # =========================================================
    # TAB 3: FINAL INTELLIGENCE REPORT
    # =========================================================
    with tab_report:
        # HEADER
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 40px; padding: 40px; background: radial-gradient(circle at center, rgba(79, 70, 229, 0.15) 0%, rgba(0,0,0,0) 70%);">
                <h2 style="background: linear-gradient(to right, #818CF8, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 3rem; margin-bottom: 10px;">FINAL INTELLIGENCE REPORT</h2>
                <p style="color: #94A3B8; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">confidential • ai-generated • strategic analysis</p>
            </div>
            """, unsafe_allow_html=True
        )

        # 1. EXECUTIVE SUMMARY & HERO METRICS
        c_hero1, c_hero2 = st.columns([1.5, 1])
        
        with c_hero1:
            st.markdown("### 📝 Executive Summary")
            
            # Dynamic Text Generation
            summary_tone = "Strong" if stats['overall'] > 75 else "Developing"
            top_strengths = [s[:15] for s in resume_skills[:3]]
            major_gaps = [g['jd_skill'] for g in jd_details if g['category'] == 'Low Match'][:2]
            
            summary_text = f"""
            <div style="font-size:1.05rem; line-height:1.7; color:#cbd5e1; margin-bottom:20px;">
                The candidate demonstrates a <strong>{summary_tone}</strong> alignment with the target role. 
                Key strengths identified in <strong>{', '.join(top_strengths)}</strong> provide a solid foundation. 
                However, to maximize hireability, immediate focus should be directed towards bridging gaps in 
                <span style="color:#ef4444; font-weight:600;">{', '.join(major_gaps) if major_gaps else 'advanced concepts'}</span>.
                <br><br>
                Our AI models project that completing the recommended 4-week roadmap could increase the match score by 
                <span style="color:#10b981; font-weight:700;">+{int((100 - stats['overall']) * 0.7)}%</span>.
            </div>
            """
            st.markdown(summary_text, unsafe_allow_html=True)
            
            # Recruiter Persona
            st.markdown(
                """
                <div style="background:rgba(255,255,255,0.03); border-left:4px solid #8B5CF6; padding:15px; border-radius:0 8px 8px 0;">
                    <div style="font-size:0.8rem; text-transform:uppercase; color:#8B5CF6; font-weight:700; margin-bottom:5px;">🤖 AI Recruiter Note</div>
                    <div style="font-style:italic; color:#94a3b8;">"Candidate shows promise but may be filtered out by strict ATS screens due to missing keywords. Resume structure is good, but density of technical terms needs optimization."</div>
                </div>
                """, unsafe_allow_html=True
            )

        with c_hero2:
            # Salary & Value Card
            market_val = "120k" if stats['overall'] > 80 else "95k"
            st.markdown(textwrap.dedent(f"""\
                <div style="background: linear-gradient(145deg, #1e1b4b, #0f172a); border: 1px solid #312e81; padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.3);">
                    <div style="margin-bottom:5px; color:#a5b4fc; font-size:0.9rem; letter-spacing:1px; text-transform:uppercase;">Estimated Market Value</div>
                    <div style="font-size:3.5rem; font-weight:800; color:white; margin-bottom:5px;">${market_val}</div>
                    <div style="font-size:0.8rem; color:#6366f1; background:rgba(99, 102, 241, 0.1); display:inline-block; padding:4px 12px; border-radius:12px;">Yearly Compensation</div>
                    <div style="margin-top:20px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-around;">
                    <div>
                    <div style="font-size:1.2rem; font-weight:700; color:#10b981;">To Top 10%</div>
                    <div style="font-size:0.7rem; color:#94a3b8;">Target</div>
                    </div>
                    <div>
                    <div style="font-size:1.2rem; font-weight:700; color:#f59e0b;">{stats['overall']}%</div>
                    <div style="font-size:0.7rem; color:#94a3b8;">Current</div>
                    </div>
                    </div>
                </div>
            """), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
<div style="display:flex; align-items:center; gap:15px; margin-bottom:30px;">
<div style="font-size:2.2rem; filter: drop-shadow(0 0 10px rgba(167, 139, 250, 0.5));">🧠</div>
<h3 style="margin:0; background: linear-gradient(90deg, #A78BFA, #F472B6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:2rem; letter-spacing:-1px;">Deep Dive Analytics</h3>
</div>
""", unsafe_allow_html=True
        )
        
        c_deep1, c_deep2 = st.columns(2)
        
        with c_deep1:
            st.markdown(
                """
<div style="background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5); position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; right: 0; width: 150px; height: 150px; background: radial-gradient(circle, rgba(167, 139, 250, 0.15) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; pointer-events: none;"></div>

<div style="display:flex; align-items:center; gap:20px; margin-bottom:30px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:20px;">
<div style="background: linear-gradient(135deg, #8b5cf6, #6d28d9); width:56px; height:56px; border-radius: 16px; display:flex; align-items:center; justify-content:center; font-size:1.8rem; box-shadow: 0 8px 16px rgba(109, 40, 217, 0.4); text-shadow: 0 2px 4px rgba(0,0,0,0.2);">🎤</div>
<div>
<h4 style="margin:0; color:#f8fafc; font-size:1.3rem; font-weight:700; letter-spacing:-0.5px;">Smart Interview AI</h4>
<p style="margin:4px 0 0 0; color:#94a3b8; font-size:0.9rem;">Predicted questions tailored to your profile.</p>
</div>
</div>
""", unsafe_allow_html=True
            )
            
            if "m4_data" in st.session_state and "questions" in st.session_state["m4_data"]:
                questions = st.session_state["m4_data"]["questions"]
            else:
                questions = []
                if "python" in [g.lower() for g in all_gaps]:
                    questions.append(("🐍 Python Core", "Explain the difference between list and tuple?"))
                if "react" in [g.lower() for g in all_gaps]:
                    questions.append(("⚛️ React.js", "What is the Virtual DOM and reconciliation?"))
                if "aws" in [g.lower() for g in all_gaps]:
                    questions.append(("☁️ Cloud Arch", "Explain the use case for S3 vs EBS?"))
                
                if len(questions) < 3:
                    questions.extend([
                        ("🏗️ System Design", "Describe a challenging project you engineered."),
                        ("🔗 API Design", "How do you handle API 4xx vs 5xx error states?"),
                        ("📐 Architecture", "Explain RESTful architecture principles.")
                    ])
            
            q_html = ""
            for tag, q in questions[:3]:
                q_html += f"""
<div style="margin-bottom:20px; group; height: 100%;">
<div style="display: flex; align-items: center; margin-bottom: 8px;">
<span style="background: linear-gradient(90deg, #8b5cf6, #d946ef); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size:0.75rem; font-weight:800; text-transform: uppercase; letter-spacing: 0.5px;">{tag}</span>
</div>
<div style="background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); padding: 18px 20px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); transition: transform 0.2s, background 0.2s;">
<div style="font-size:1rem; color:#e2e8f0; font-weight:500; line-height:1.5;">"{q}"</div>
</div>
</div>
"""
            st.markdown(q_html + "</div>", unsafe_allow_html=True)

        with c_deep2:
            st.markdown(
                """
<div style="background: linear-gradient(160deg, #0f172a 0%, #022c22 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5); position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; right: 0; width: 150px; height: 150px; background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; pointer-events: none;"></div>

<div style="display:flex; align-items:center; gap:20px; margin-bottom:30px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:20px;">
<div style="background: linear-gradient(135deg, #10b981, #059669); width:56px; height:56px; border-radius: 16px; display:flex; align-items:center; justify-content:center; font-size:1.8rem; box-shadow: 0 8px 16px rgba(16, 185, 129, 0.4); text-shadow: 0 2px 4px rgba(0,0,0,0.2);">🏢</div>
<div>
<h4 style="margin:0; color:#f8fafc; font-size:1.3rem; font-weight:700; letter-spacing:-0.5px;">Company Tier Match</h4>
<p style="margin:4px 0 0 0; color:#94a3b8; font-size:0.9rem;">Where your skills strongly align.</p>
</div>
</div>
""", unsafe_allow_html=True
            )
            
            fit_score = stats['overall']
            
            tiers = [
                {"name": "FAANG / Big Tech", "threshold": 85, "color1": "#ec4899", "color2": "#be185d"},
                {"name": "Growth Stage Scaleups", "threshold": 70, "color1": "#3b82f6", "color2": "#2563eb"},
                {"name": "Early Stage Startups", "threshold": 50, "color1": "#10b981", "color2": "#059669"},
                {"name": "Freelance / Projects", "threshold": 0, "color1": "#f59e0b", "color2": "#d97706"}
            ]
            
            tier_html = ""
            for tier in tiers:
                is_match = fit_score >= tier['threshold']
                
                # Logic for status
                if fit_score >= tier['threshold'] + 20: 
                     status = "STRONG MATCH"
                     icon = "🔥"
                     opacity = "1"
                     width = "100%"
                     grad = f"linear-gradient(90deg, {tier['color1']}, {tier['color2']})"
                     text_color = tier['color1']
                elif fit_score >= tier['threshold']:
                     status = "QUALIFIED"
                     icon = "✅"
                     opacity = "1"
                     width = f"{min(100, 40 + (fit_score - tier['threshold']) * 3)}%"
                     grad = f"linear-gradient(90deg, {tier['color1']}, {tier['color2']})"
                     text_color = tier['color1']
                else:
                     status = "GAP DETECTED"
                     icon = "⚠️"
                     opacity = "0.9" 
                     width = "100%"
                     grad = "rgba(239, 68, 68, 0.15)"  
                     text_color = "#ef4444"  

                tier_html += f"""
<div style="margin-bottom:24px; opacity:{opacity};">
<div style="display:flex; justify-content:space-between; margin-bottom:8px; align-items:center;">
<div style="font-weight:700; font-size:0.95rem; color:#f1f5f9; display:flex; align-items:center; gap:8px;">
{tier['name']}
</div>
<div style="font-size:0.75rem; font-weight:800; color:{text_color}; letter-spacing:0.5px; background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:6px; display:flex; align-items:center; gap:5px;">
{icon} {status}
</div>
</div>
<div style="width:100%; height:10px; background:rgba(0,0,0,0.4); border-radius:6px; overflow:hidden; border:1px solid rgba(255,255,255,0.05);">
<div style="width:{width}; height:100%; background:{grad}; border-radius:6px; box-shadow: 0 0 15px {text_color}40; transition: width 1s ease-out;"></div>
</div>
</div>
"""
            st.markdown(tier_html + "</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:15px; margin-bottom:30px;">
                <div style="font-size:2.2rem; filter: drop-shadow(0 0 10px rgba(244, 114, 182, 0.5));">🚀</div>
                <h3 style="margin:0; background: linear-gradient(90deg, #F472B6, #FB7185); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:2rem; letter-spacing:-1px;">Career Trajectory Engine</h3>
            </div>
            """, unsafe_allow_html=True
        )

        c_traj1, c_traj2 = st.columns(2)
        
        with c_traj1:
            st.markdown(
                """
<div style="background: linear-gradient(160deg, #0f172a 0%, #312e81 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);">
    <div style="display:flex; align-items:center; gap:15px; margin-bottom:25px;">
        <div style="background:rgba(244, 114, 182, 0.15); width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">🎯</div>
        <h4 style="margin:0; color:white; font-weight:700;">Role Compatibility</h4>
    </div>
    <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:20px;">Based on your current skill matrix, here are roles you are evolving towards.</p>
""", unsafe_allow_html=True
            )
            roles = [
                {"role": "Senior Developer", "match": min(95, stats['overall'] + 10)},
                {"role": "Tech Lead", "match": min(85, stats['overall'] - 5)},
                {"role": "Solutions Architect", "match": min(70, stats['overall'] - 20)}
            ]
            
            role_html = ""
            for r in roles:
                r_match = max(0, r['match'])
                color = "#f472b6" if r_match > 80 else "#a78bfa" if r_match > 60 else "#64748b"
                role_html += f"""
<div style="margin-bottom:15px;">
    <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.9rem; font-weight:600; color:#e2e8f0;">
        <span>{r['role']}</span>
        <span style="color:{color};">{r_match}%</span>
    </div>
    <div style="width:100%; height:6px; background:rgba(0,0,0,0.3); border-radius:3px;">
        <div style="width:{r_match}%; height:100%; background:{color}; border-radius:3px; box-shadow:0 0 10px {color}60;"></div>
    </div>
</div>
"""
            st.markdown(role_html + "</div>", unsafe_allow_html=True)
            
        with c_traj2:
            st.markdown(
                """
<div style="background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);">
    <div style="display:flex; align-items:center; gap:15px; margin-bottom:25px;">
        <div style="background:rgba(56, 189, 248, 0.15); width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">📈</div>
        <h4 style="margin:0; color:white; font-weight:700;">Salary Uplift Projection</h4>
    </div>
    <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:20px;">Estimated market value increase after closing identified gaps.</p>
""", unsafe_allow_html=True
            )
            
            # Simple simulation logic
            current_est = 85000 + (stats['overall'] * 500)
            potential_est = current_est * 1.35  
            
            st.markdown(textwrap.dedent(f"""\
                <div style="display:flex; flex-direction:column; gap:20px; margin-top:10px;">
                    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; border-left:4px solid #94a3b8;">
                        <div style="font-size:0.85rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">Current Estimate</div>
                        <div style="font-size:1.5rem; color:#f8fafc; font-weight:800;">${current_est:,.0f} <span style="font-size:0.9rem; color:#64748b; font-weight:500;">/ yr</span></div>
                    </div>
                    <div style="background:rgba(16, 185, 129, 0.1); padding:15px; border-radius:12px; border-left:4px solid #10b981; position:relative; overflow:hidden;">
                        <div style="position:absolute; right:-10px; top:-10px; font-size:3rem; opacity:0.1;">💰</div>
                        <div style="font-size:0.85rem; color:#10b981; text-transform:uppercase; font-weight:700;">Projected Potential</div>
                        <div style="font-size:1.8rem; color:#10b981; font-weight:800; text-shadow: 0 0 20px rgba(16,185,129,0.3);">${potential_est:,.0f} <span style="font-size:0.9rem; font-weight:500;">/ yr</span></div>
                        <div style="margin-top:5px; font-size:0.8rem; color:#10b981; font-weight:600;">+35% Growth Opportunity</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:15px; margin-bottom:30px;">
                <div style="font-size:2.2rem; filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.5));">🔮</div>
                <h3 style="margin:0; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:2rem; letter-spacing:-1px;">Future-Proofing & Market Intelligence</h3>
            </div>
            """, unsafe_allow_html=True
        )
        
        c_fut1, c_fut2 = st.columns(2)
        
        with c_fut1:
            st.markdown(
                """
<div style="background: linear-gradient(160deg, #0f172a 0%, #172554 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);">
    <div style="display:flex; align-items:center; gap:15px; margin-bottom:20px;">
        <div style="background:rgba(56, 189, 248, 0.1); width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">📊</div>
        <h4 style="margin:0; color:white; font-weight:700;">Industry Demand Heatmap</h4>
    </div>
    <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:25px; line-height:1.6;">Sectors showing the highest velocity of hiring for your specific skill cluster.</p>
""", unsafe_allow_html=True
            )
            
            industries = [
                {"name": "FinTech & Blockchain", "growth": 92, "color": "#10b981"},
                {"name": "HealthTech & BioAI", "growth": 78, "color": "#3b82f6"},
                {"name": "Enterprise SaaS", "growth": 65, "color": "#f59e0b"},
                {"name": "E-Commerce & Retail", "growth": 45, "color": "#64748b"}
            ]
            
            ind_html = ""
            for ind in industries:
                ind_html += f"""
                <div style="margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px; color:#e2e8f0; font-weight:600; font-size:0.9rem;">
                        <span>{ind['name']}</span>
                        <span style="color:{ind['color']};">+{ind['growth']}% Growth</span>
                    </div>
                    <div style="width:100%; height:8px; background:rgba(255,255,255,0.05); border-radius:4px; overflow:hidden;">
                        <div style="width:{ind['growth']}%; height:100%; background:{ind['color']}; border-radius:4px; box-shadow: 0 0 10px {ind['color']}40;"></div>
                    </div>
                </div>
                """
            
            st.markdown(ind_html + "</div>", unsafe_allow_html=True)

        with c_fut2:
            st.markdown(
                """<div style="background: linear-gradient(160deg, #0f172a 0%, #312e81 100%); border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);">
<div style="display:flex; align-items:center; gap:15px; margin-bottom:20px;">
<div style="background:rgba(236, 72, 153, 0.1); width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">🎓</div>
<h4 style="margin:0; color:white; font-weight:700;">Certification ROI Calculator</h4>
</div>
<p style="color:#cbd5e1; font-size:0.95rem; margin-bottom:20px; line-height:1.6;">Projected salary impact of acquiring top-tier certifications.</p>
<div style="display:grid; grid-template-columns: 1fr; gap:15px;">
<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); display:flex; align-items:center; gap:15px;">
<div style="background:#FFF; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:bold; color:#f59e0b;">☁️</div>
<div style="flex-grow:1;">
<div style="color:#f8fafc; font-weight:700; font-size:0.95rem;">AWS Solutions Architect</div>
<div style="color:#94a3b8; font-size:0.8rem;">Cloud Mastery</div>
</div>
<div style="text-align:right;">
<div style="color:#10b981; font-weight:800; font-size:1.1rem;">+$12k</div>
<div style="color:#64748b; font-size:0.7rem;">/ year</div>
</div>
</div>
<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); display:flex; align-items:center; gap:15px;">
<div style="background:#FFF; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:bold; color:#3b82f6;">🐍</div>
<div style="flex-grow:1;">
<div style="color:#f8fafc; font-weight:700; font-size:0.95rem;">TensorFlow Developer</div>
<div style="color:#94a3b8; font-size:0.8rem;">AI Specialization</div>
</div>
<div style="text-align:right;">
<div style="color:#10b981; font-weight:800; font-size:1.1rem;">+$15k</div>
<div style="color:#64748b; font-size:0.7rem;">/ year</div>
</div>
</div>
<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); display:flex; align-items:center; gap:15px;">
<div style="background:#FFF; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:bold; color:#6366f1;">⚓</div>
<div style="flex-grow:1;">
<div style="color:#f8fafc; font-weight:700; font-size:0.95rem;">CKA (Kubernetes)</div>
<div style="color:#94a3b8; font-size:0.8rem;">DevOps Pro</div>
</div>
<div style="text-align:right;">
<div style="color:#10b981; font-weight:800; font-size:1.1rem;">+$18k</div>
<div style="color:#64748b; font-size:0.7rem;">/ year</div>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br><br><br><br>", unsafe_allow_html=True) 
        st.markdown(
            """
            <div style="background: linear-gradient(90deg, #4338ca, #3730a3); padding: 40px; border-radius: 20px; text-align: center; color: white; margin-top: 30px; margin-bottom: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">📑</div>
                <h2 style="color:white; margin:0 0 10px 0; font-size: 1.8rem;">Download Comprehensive Report</h2>
                <p style="opacity:0.9; margin-bottom:0; font-size: 1rem;">Get the full 5-page analysis including charts, roadmap, and deep-dive metrics.</p>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)  
        
        # Center the button
        _, c_dl, _ = st.columns([1, 2, 1])
         
        with c_dl:
            # Check session state for persistence
            if "full_report_pdf" in st.session_state:
                st.download_button(
                    "⬇️ Download Comprehensive Report (PDF)", 
                    st.session_state["full_report_pdf"], 
                    "SkillGap_Intelligence_Report.pdf", 
                    "application/pdf", 
                    use_container_width=True,
                    key="dl_btn_full_report_persistent"
                )
                if st.button("🔄 Regenerate Report", type="secondary", use_container_width=True):
                    del st.session_state["full_report_pdf"]
                    st.rerun()
            else:
                if st.button("Generate & Download Full Report (PDF)", type="primary", use_container_width=True):
                     with st.spinner("Compiling Intelligence Report (Adding Roadmaps, Projects, & Salary Data)..."):
                        
                        pdf_projects = projects if 'projects' in locals() else []
                        pdf_soft_skills = actions if 'actions' in locals() else []
                        
                        chunk_size = math.ceil(len(all_gaps) / 3)
                        w1 = all_gaps[:chunk_size]
                        w2 = all_gaps[chunk_size:chunk_size*2]
                        w3 = all_gaps[chunk_size*2:]
                        roadmap_weeks_pdf = [
                            {"title": "Week 1", "focus": w1, "desc": "Foundations", "tasks": []},
                            {"title": "Week 2", "focus": w2, "desc": "Application", "tasks": []},
                            {"title": "Week 3", "focus": w3, "desc": "Integration", "tasks": []},
                            {"title": "Week 4", "focus": ["Interview"], "desc": "Mastery", "tasks": []}
                        ]
                        
                        try:
                            pdf_bytes = create_full_report_pdf(
                                stats, 
                                jd_details, 
                                missing_kws, 
                                roadmap_weeks_pdf,
                                project_ideas=pdf_projects,
                                soft_skills=pdf_soft_skills
                            )
                            st.session_state["full_report_pdf"] = pdf_bytes
                            
                        except Exception as e:
                            st.error(f"Error generating report: {e}")
        

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🚀 Next Steps")
    
    col_next1, col_next2 = st.columns(2)
    
    with col_next1:
        st.markdown(
            """
            <div style="background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid #312e81; padding: 40px 20px; border-radius: 16px; text-align: center; height: 240px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 3.5rem; margin-bottom: 15px; filter: drop-shadow(0 0 15px rgba(129, 140, 248, 0.3));">💭</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 8px;">Share Your Thoughts</div>
                <div style="color: #94A3B8; font-size: 0.95rem; max-width: 320px; margin: 0 auto; line-height: 1.5;">Help us improve SkillGapAI by sharing your feedback on this analysis.</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)  
        from components import navigate_to
        st.button("Give Feedback", type="secondary", use_container_width=True, on_click=navigate_to, args=("Feedback",))
            
    with col_next2:
        st.markdown(
            """
            <div style="background: linear-gradient(180deg, #022c22 0%, #064e3b 100%); border: 1px solid #059669; padding: 40px 20px; border-radius: 16px; text-align: center; height: 240px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.3);">
                <div style="font-size: 3.5rem; margin-bottom: 15px; filter: drop-shadow(0 0 15px rgba(52, 211, 153, 0.3));">📬</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 8px;">Get in Touch</div>
                <div style="color: #94A3B8; font-size: 0.95rem; max-width: 320px; margin: 0 auto; line-height: 1.5;">Have questions about your report? Contact our support team.</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)  
        st.button("Contact Us", type="primary", use_container_width=True, on_click=navigate_to, args=("Contact Us",))

    # -------------------------
    # BACK NAVIGATION BAR
    # -------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""\
        <div style="background: linear-gradient(90deg, #475569, #334155); padding: 25px; border-radius: 16px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); border: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 2.5rem; background: rgba(255,255,255,0.1); width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 50%;">🔙</div>
                <div>
                    <div style="font-weight: 800; font-size: 1.4rem; margin-bottom: 4px;">Refine Analysis?</div>
                    <div style="font-size: 1rem; opacity: 0.8;">Return to Milestone 3 to adjust simulation parameters or critical skills.</div>
                </div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.5;">↩️</div>
        </div>
        """),
        unsafe_allow_html=True,
    )
    st.button("← Return to Milestone 3", type="primary", use_container_width=True, on_click=navigate_to, args=("Milestone 3: Gap Analysis",))

    ui_components.render_footer()


if __name__ == "__main__":
    st.set_page_config(page_title="Milestone 4", layout="wide")
    app()
