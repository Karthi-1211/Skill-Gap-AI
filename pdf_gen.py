import io
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import datetime

# ------------------------------------------------------------------------------
# 1. MILESTONE 4 REPORT GENERATION
# ------------------------------------------------------------------------------

def create_full_report_pdf(stats, jd_details, missing_kws, roadmap_weeks, project_ideas=[], soft_skills=[]):
    """
    Generates a premium, magazine-style Full Intelligence Report PDF.
    Includes: Cover Page, Visual Executive Summary, Deep Dive Roadmap, and Strategic Recommendations.
    """
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

    # --- CUSTOM STYLES ---
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
    
    # 1. Score Cards
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

    # 2. Analysis Text
    story.append(Paragraph("Strategic Analysis", ParagraphStyle('H3', parent=s_header, fontSize=14)))
    analysis_text = f"Based on the job description analysis, your profile demonstrates strong alignment in core areas. However, <b>{len(missing_kws)} specific high-value keywords</b> were identified as missing or under-represented. Closing these gaps is projected to increase your interview probability by approximately <b>40%</b>."
    story.append(Paragraph(analysis_text, s_body))
    story.append(Spacer(1, 20))

    # 3. Missing Skills
    story.append(Paragraph("High-Priority Missing Skills", ParagraphStyle('H3', parent=s_header, fontSize=14)))
    
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
    story.append(Spacer(1, 20))

    if project_ideas:
        story.append(Paragraph("Recommended Capstone Projects", ParagraphStyle('H3', parent=s_header, fontSize=14)))
        for p in project_ideas:
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
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ]))
        story.append(t_soft)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_template_css(template_name):
    """Returns the CSS string for the specified template."""
    
    # Common Reset & Base
    base_css = """
    @page {
        size: a4 portrait;
        margin: 0cm;
        background-color: white;
    }
    body {
        font-family: 'Helvetica', sans-serif;
        color: #333;
        line-height: 1.35;
        margin: 0;
        padding: 0;
        background-color: white;
    }
    html { }
    .container {
        padding: 25px;  
    }
    h1, h2, h3, h4 { margin: 0; padding: 0; }
    ul { padding-left: 18px; margin: 3px 0; }
    li { margin-bottom: 1px; }
    .section-title {
        text-transform: uppercase;
        font-weight: bold;
        border-bottom: 1px solid #ccc;
        margin-top: 15px;
        margin-bottom: 8px;
        padding-bottom: 2px;
        font-size: 13px;
    }
    .item-header {
        font-weight: bold;
        font-size: 13px;
    }
    .item-sub {
        font-style: italic;
        color: #666;
        font-size: 11px;
    }
    .date-loc {
        float: right;
        font-size: 11px;
        color: #666;
    }
    """
    
    if template_name == "Ivy League":
        return base_css + """
        body { font-family: 'Times New Roman', serif; }
        .name { text-align: center; font-size: 28px; text-transform: uppercase; letter-spacing: 2px; }
        .contact { text-align: center; font-size: 12px; margin-bottom: 20px; }
        .section-title { border-bottom: 1px solid #000; text-align: center; }
        """
    
    elif template_name == "Minimal":
        return base_css + """
        body { font-family: 'Helvetica', sans-serif; }
        .name { font-size: 32px; font-weight: 800; letter-spacing: -1px; }
        .contact { color: #666; font-size: 12px; margin-top: 5px; margin-bottom: 30px; }
        .section-title { border-bottom: 2px solid #333; font-size: 12px; letter-spacing: 1px; }
        """
        
    elif template_name == "Modern":
        return base_css + """
        body { font-family: 'Helvetica', sans-serif; }
        .header-bg {
            background-color: #2563eb;
            color: white;
            padding: 40px;
            margin: -40px -40px 30px -40px; /* Bleed to edge */
        }
        .name { font-size: 36px; font-weight: bold; color: white; }
        .role { font-size: 18px; opacity: 0.9; color: white; margin-top: 5px; }
        .contact { color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 10px; }
        .section-title { color: #2563eb; border-bottom: 2px solid #2563eb; }
        """
        
    if template_name == "Creative":
        return base_css + """
        /* Two column layout simulated with tables for PDF */
        body { font-family: 'Helvetica', sans-serif; }
        .container { padding: 0 !important; }
        .sidebar {
            background-color: #7c3aed;
            color: white;
            padding: 30px;
            vertical-align: top;
        }
        .main-content {
            padding: 30px;
            vertical-align: top;
        }
        .name { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
        .role { color: #7c3aed; font-weight: bold; font-size: 14px; margin-bottom: 20px; }
        .sb-section { margin-bottom: 20px; }
        .sb-title { font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 5px; margin-bottom: 10px; font-size: 14px; }
        .sb-item { font-size: 12px; margin-bottom: 5px; }
        """
    
    return base_css

def get_html_structure(data, template_name):
    """Generates the HTML body based on the template."""
    
    # Data extraction for easier usage
    name = data.get("name", "Your Name")
    role = data.get("role", "Professional Role")
    email = data.get("email", "")
    phone = data.get("phone", "")
    summary = data.get("summary", "")
    skills = data.get("skills", [])
    exp = data.get("experience", [])
    edu = data.get("education", [])
    proj = data.get("projects", [])
    achievements = data.get("achievements", "")
    
    contact_info = f"{email} | {phone}"
    if data.get("linkedin"): contact_info += f" | {data['linkedin']}"
    if data.get("github"): contact_info += f" | {data['github']}"

    # Helper: Convert newlines to Bullet Points
    def format_as_bullets(text):
        if not text: return ""
        # Split by newline
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines: return ""
        
        # Build HTML list
        list_html = "<ul>"
        for line in lines:
            clean = line.lstrip('•-* ').strip()
            list_html += f"<li>{clean}</li>"
        list_html += "</ul>"
        return list_html

    # Helper for Experience Items
    def render_exp(items):
        html = ""
        for item in items:
            title = item.get('title', '')
            company = item.get('company', '')
            dur = item.get('duration', '')
            raw_desc = item.get('desc', '')
            
            # Use bullet formatter
            desc_html = format_as_bullets(raw_desc)
            
            html += f"""
            <div style="margin-bottom: 10px;">
                <div style="clear:both;">
                    <span class="item-header">{title}</span>, <span class="item-sub">{company}</span>
                    <span class="date-loc">{dur}</span>
                </div>
                <div style="font-size:11px; margin-top:2px;">{desc_html}</div>
            </div>
            """
        return html

    # Helper for Projects
    def render_projs(items):
        html = ""
        for item in items:
            title = item.get('title', '')
            tech = ", ".join(item.get('tech', []))
            raw_desc = item.get('desc', '')
            
            # Use bullet formatter
            desc_html = format_as_bullets(raw_desc)
            
            html += f"""
            <div style="margin-bottom: 8px;">
                <div class="item-header">{title} <span style="font-weight:normal; font-size:10px; color:#666;">({tech})</span></div>
                <div style="font-size:11px;">{desc_html}</div>
            </div>
            """
        return html
    
    # Helper for Education
    def render_edu(items):
        html = ""
        for item in items:
            school = item.get('school', '')
            degree = item.get('degree', '')
            year = item.get('year', '')
            html += f"""
            <div style="margin-bottom: 8px;">
                <div style="clear:both;">
                    <span class="item-header">{school}</span>
                    <span class="date-loc">{year}</span>
                </div>
                <div class="item-sub">{degree}</div>
            </div>
            """
        return html

    # Helper for Skills
    def render_skills(items):
        skill_txt = ""
        if items and isinstance(items[0], dict):
             parts = []
             for s in items:
                 parts.append(f"<b>{s.get('category','')}:</b> {s.get('items','')}")
             skill_txt = "<br/>".join(parts)
        else:
             skill_txt = ", ".join(items) if items else ""
        return f"<div style='font-size:11px;'>{skill_txt}</div>"

    # Helper for Achievements
    def render_achievements(text):
        if not text: return ""
        return f"<div style='font-size:11px;'>{format_as_bullets(text)}</div>"

    # Helper for Certifications
    def render_certs(items):
        if not items: return ""
        html = ""
        for item in items:
            name = item.get('name', '')
            auth = item.get('authority', '')
            year = item.get('year', '')
            
            meta = []
            if auth: meta.append(auth)
            if year: meta.append(year)
            meta_str = " - ".join(meta)
            
            html += f"""
            <div style="margin-bottom: 4px;">
                <span class="item-header" style="font-size:11px;">{name}</span>
                <span class="item-sub" style="margin-left:5px; font-size:10px;">{meta_str}</span>
            </div>
            """
        return html
    
    if template_name == "Creative":
        # Two Column Table Layout
        sb_skills = render_skills(skills)
        sb_contact = f"<div>{email}</div><div>{phone}</div><div>{data.get('linkedin','')}</div>"
        
        ach_html = ""
        if achievements:
            ach_html = f"""
            <div style="margin-bottom: 20px;">
                <div class="section-title">Achievements</div>
                {render_achievements(achievements)}
             </div>
            """
            
        cert_html = ""
        if data.get("certifications"):
             cert_html = f"""
             <div class="section-title">Certifications</div>
             {render_certs(data['certifications'])}
             """

        return f"""
        <div class="container">
        <table style="width:100%; height:100%; border-spacing: 0;">
            <tr>
                <td class="sidebar" width="30%">
                     <div class="name" style="color:white; font-size:22px;">{name}</div>
                     <div style="color:rgba(255,255,255,0.8); margin-bottom:30px;">{role}</div>
                     
                     <div class="sb-section">
                        <div class="sb-title">CONTACT</div>
                        <div class="sb-item">{sb_contact}</div>
                     </div>
                     
                     <div class="sb-section">
                        <div class="sb-title">EDUCATION</div>
                        <div class="sb-item">{render_edu(edu)}</div>
                     </div>
                     
                     <div class="sb-section">
                        <div class="sb-title">SKILLS</div>
                        <div class="sb-item">{sb_skills}</div>
                     </div>
                </td>
                <td class="main-content" width="70%">
                     <div style="margin-bottom: 20px;">
                        <div class="section-title">Professional Summary</div>
                        <div style="font-size:11px;">{summary}</div>
                     </div>
                     
                     <div style="margin-bottom: 20px;">
                        <div class="section-title">Experience</div>
                        {render_exp(exp)}
                     </div>
                     
                     <div style="margin-bottom: 20px;">
                        <div class="section-title">Projects</div>
                        {render_projs(proj)}
                     </div>
                     
                     {ach_html}
                     {cert_html}
                </td>
            </tr>
        </table>
        </div>
        """
        
    elif template_name == "Modern":
        # Header Box + Main Content
        ach_html = ""
        if achievements:
            ach_html = f"""<div class="section-title">Achievements</div>
            {render_achievements(achievements)}
            <div style="margin-bottom:20px;"></div>"""

        cert_html = ""
        if data.get("certifications"):
            cert_html = f"""<div class="section-title">Certifications</div>
            {render_certs(data['certifications'])}
            <div style="margin-bottom:20px;"></div>"""
            
        return f"""
        <div class="container">
            <div class="header-bg">
                <div class="name">{name}</div>
                <div class="role">{role}</div>
                <div class="contact">{contact_info}</div>
            </div>
            
            <div class="section-title">Professional Summary</div>
            <div style="font-size:11px; margin-bottom:12px;">{summary}</div>
            
            <div class="section-title">Education</div>
            {render_edu(edu)}
            
            <div class="section-title">Skills</div>
            {render_skills(skills)}
            <div style="margin-bottom:20px;"></div>

            <div class="section-title">Experience</div>
            {render_exp(exp)}
            
            <div class="section-title">Projects</div>
            {render_projs(proj)}
            
            {ach_html}
            {cert_html}
        </div>
        """
    
    else: 
        alignment_class = "text-align:center;" if template_name == "Ivy League" else ""
        
        ach_html = ""
        if achievements:
            ach_html = f"""<div class="section-title">Achievements</div>
            {render_achievements(achievements)}"""
            
        cert_html = ""
        if data.get("certifications"):
            cert_html = f"""<div class="section-title">Certifications</div>
            {render_certs(data['certifications'])}"""
        
        return f"""
        <div class="container">
            <div class="name">{name}</div>
            <div style="{alignment_class} margin-bottom:5px;">{role}</div>
            <div class="contact">{contact_info}</div>
            
            <div class="section-title">Professional Summary</div>
            <div style="font-size:11px; margin-bottom:12px;">{summary}</div>
            
            <div class="section-title">Education</div>
            {render_edu(edu)}
            
            <div class="section-title">Skills</div>
            {render_skills(skills)}
            
            <div class="section-title">Experience</div>
            {render_exp(exp)}
            
            <div class="section-title">Projects</div>
            {render_projs(proj)}
            
            {ach_html}
            {cert_html}
        </div>
        """

def render_resume_html(data, ui_config, is_preview=False):
    """
    Renders the HTML for the resume. 
    If is_preview is True, it might optimize for Web view, but since we want fidelity, 
    we keep it close to PDF structure.
    """
    if isinstance(ui_config, str):
        template_name = ui_config
    else:
        template_name = ui_config.get("template", "Ivy League")
        
    css = get_template_css(template_name)
    html_body = get_html_structure(data, template_name)
    
    preview_style = ""
    if is_preview:
        preview_style = """
        <style>
            body {
                background-color: #525659; 
                display: flex;
                justify-content: center;
                padding: 40px 0;
            }
            .container {
                width: 210mm;
                min-height: 297mm;
                background-color: white;
                box-shadow: 0 0 15px rgba(0,0,0,0.5);
                margin: 0 auto;
                box-sizing: border-box;
                overflow: hidden; 
            }
            /* Force full height table in preview */
            table { height: 100%; }
        </style>
        """

    full_html = f"""
    <html>
    <head>
        <style>{css}</style>
        {preview_style}
    </head>
    <body class="{'preview-mode' if is_preview else ''}">
        {html_body}
    </body>
    </html>
    """
    return full_html

def get_client_side_pdf_html(data, template_name):
    """
    Generates an HTML page with embedded JS to render the PDF client-side.
    Rewritten to use basic string concatenation to avoid SyntaxErrors.
    """
    resume_html = render_resume_html(data, template_name)
    clean_name = data.get("name", "Resume").replace(" ", "_")
    
    css = get_template_css(template_name)
    body_content = get_html_structure(data, template_name)
    
    pdf_content = (
        '<div id="resume-content" style="background: white; width: 210mm; min-height: 297mm; padding: 0; margin: 0 auto;">'
        + body_content +
        '</div>'
    )
    
    # Header
    html_start = (
        '<!DOCTYPE html>'
        '<html>'
        '<head>'
        '<meta charset="utf-8" />'
        '<title>Generating PDF...</title>'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>'
        '<style>'
        + css +
        'body { background-color: #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 50px; font-family: sans-serif; }'
        '#generating-msg { font-size: 20px; color: #333; margin-bottom: 20px; }'
        '</style>'
        '</head>'
        '<body>'
        '<div id="generating-msg">Generating High-Fidelity PDF... (Please wait)</div>'
    )
    
    # Script parts - formatted carefully to insert variable
    js_filename = f"'{clean_name}_Resume.pdf'"
    
    js_code = (
        '<script>'
        'window.onload = function() {'
        "    const element = document.getElementById('resume-content');"
        '    const opt = {'
        '        margin:       0,'
        '        filename:     ' + js_filename + ','
        "        image:        { type: 'jpeg', quality: 0.98 },"
        "        html2canvas:  { scale: 2, useCORS: true },"
        "        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }"
        '    };'
        '    html2pdf().set(opt).from(element).save().then(function(){'
        '        document.getElementById("generating-msg").innerText = "SUCCESS: PDF Downloaded! You can close this tab.";'
        '    });'
        '};'
        '</script>'
    )
    
    # Assemble
    full_page = html_start + pdf_content + js_code + "</body></html>"
    return full_page