import io
import re
import json
import tempfile
from typing import Tuple, List
from datetime import datetime

import streamlit as st
from pypdf import PdfReader
import docx2txt
import pandas as pd
import streamlit.components.v1 as components

# spaCy optional
try:
    import spacy
    from spacy.matcher import PhraseMatcher
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

# PDF generation: try to import reportlab
_REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    _REPORTLAB_AVAILABLE = True
except Exception:
    _REPORTLAB_AVAILABLE = False

st.set_page_config(page_title="SkillGapAI — Milestone 1", page_icon="🧭", layout="wide")

# -------------------------
# Sidebar (settings) - ENHANCED
# -------------------------
# Ensure containers for later file-name updates
if "resume_file_name" not in st.session_state:
    st.session_state["resume_file_name"] = ""
if "jd_file_name" not in st.session_state:
    st.session_state["jd_file_name"] = ""
if "custom_skills" not in st.session_state:
    st.session_state["custom_skills"] = []
if "app_version" not in st.session_state:
    st.session_state["app_version"] = "1.0.0"
if "app_stats" not in st.session_state:
    # placeholder counters; you can wire these to real metrics later
    st.session_state["app_stats"] = {"sessions_today": 1, "files_parsed": 0, "skills_detected": 0}
if "debug_logs" not in st.session_state:
    st.session_state["debug_logs"] = False
if "experimental" not in st.session_state:
    st.session_state["experimental"] = False

with st.sidebar:
    # Logo & tagline
    st.markdown(
        """
        <div style='text-align:center; padding:8px 0;'>
            <div style='width:64px;height:64px;margin:0 auto;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;
                        background:linear-gradient(135deg,#06b6d4,#3b82f6);color:#fff;
                        font-weight:800;box-shadow:0 6px 18px rgba(0,0,0,0.08);'>SG</div>
            <div style='margin-top:8px;font-size:14px;font-weight:700;'>SkillGapAI</div>
            <div style='font-size:12px;color:#94a3b8;margin-top:4px;'>Compare resumes • Highlight gaps • Export</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.header("Settings & Helpers")

    # Theme + accent controls
    theme_mode = st.radio("Theme", options=["Dark", "Light"], index=0)
    # allow accent customization for light theme
    accent_color = st.color_picker("Accent color", value="#1e40af") if theme_mode == "Light" else "#06b6d4"

    auto_parse = st.checkbox("Auto-parse on upload/paste", value=True)
    show_skill_highlights = st.checkbox("Show Skill Highlights", value=True)
    st.markdown("---")

    # Quick navigation (useful once app grows)
    st.subheader("Quick Navigation")
    st.markdown(
        """
        - 📄 Resume Parser  
        - 📝 Job Description  
        - 🎯 Skill Gap Report  
        - 📊 Export Tools
        """,
        unsafe_allow_html=True,
    )

    # Samples
    st.markdown("---")
    st.markdown("Sample Templates")
    sample = st.selectbox(
        "Load a sample",
        options=["None", "Sample Resume","Software Engineer (JD)", "Data Scientist (JD)", ],
        index=0,
    )

    # Custom skills manager
    st.markdown("---")
    st.subheader("Custom Skills")
    new_skill = st.text_input("Add a skill (e.g. fastapi)")
    add_clicked = st.button("Add Skill", key="add_skill_btn")
    if add_clicked and new_skill.strip():
        cleaned = new_skill.strip().lower()
        if cleaned not in st.session_state["custom_skills"]:
            st.session_state["custom_skills"].append(cleaned)
    if st.session_state["custom_skills"]:
        st.markdown("*Your skills:* " + ", ".join(st.session_state["custom_skills"]))
        if st.button("Clear custom skills"):
            st.session_state["custom_skills"] = []

    # Advanced settings in an expander
    with st.expander("Advanced Settings"):
        st.checkbox("Enable Debug Logs", key="debug_logs")
        st.checkbox("Show Hidden Skill Patterns", key="show_hidden_patterns", value=False)
        st.checkbox("Enable Experimental Features", key="experimental")

    # File info (dynamically updates because of session_state)
    st.markdown("---")
    st.subheader("Uploaded Files")
    if st.session_state.get("resume_file_name"):
        st.markdown(f"📄 Resume: *{st.session_state['resume_file_name']}*")
    else:
        st.markdown("📄 Resume: not uploaded")
    if st.session_state.get("jd_file_name"):
        st.markdown(f"📝 JD: *{st.session_state['jd_file_name']}*")
    else:
        st.markdown("📝 JD: not uploaded")

    # App stats (placeholders)
    st.markdown("---")
    st.subheader("App Stats")
    stats = st.session_state["app_stats"]
    st.markdown(f"🚀 Sessions Today: *{stats['sessions_today']}*  ")
    st.markdown(f"📄 Files Parsed: *{stats['files_parsed']}*  ")
    st.markdown(f"🧠 Skills Detected: *{stats['skills_detected']}*  ")

    # Version switcher & support
    st.markdown("---")
    st.selectbox("App Version", ["1.0.0", "1.0.2", "1.0.3", "1.0.4"], index=0, key="app_version")
    st.markdown("---")
    st.subheader("Support")
    st.markdown("• Email: balukarthikalamanda@gmail.com  ")
    st.markdown("• Docs: https://example.com/docs  ")
    st.markdown("---")

    # Footer note in sidebar
    st.markdown("<div style='text-align:center;color:#94a3b8;font-size:12px;padding-top:6px'>Developed with ❤ by Balu Karthik</div>", unsafe_allow_html=True)

# -------------------------
# Theme / CSS
# -------------------------
# Keep dark theme from v3 unchanged (user likes it). Improve the light theme substantially.
ACCENT = "#3b82f6"
# if a custom accent_color is set in sidebar, prefer it for light theme
if theme_mode == "Dark":
    BODY_BG = "linear-gradient(180deg, #0f172a 0%, #071032 35%, #041126 100%)"
    SIDEBAR_BG = "rgba(15, 23, 42, 0.8)"  # dark sidebar for dark theme
    TEXT_COLOR = "#e6eef8"
    CARD_BG = "linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))"
    MUTED = "#9fb0d4"
else:
    # Professional light theme: high contrast, excellent readability
    ACCENT = accent_color or "#1e40af"  # use picked accent
    BODY_BG = "#e5e7eb"
    SIDEBAR_BG = "#f3f4f6"
    TEXT_COLOR = "#111827"
    CARD_BG = "#ffffff"
    MUTED = "#6b7280"

# Additional light-theme tweaks (buttons / minor accent overrides)
LIGHT_BUTTON_BG = f"linear-gradient(135deg, {ACCENT}, #111827)" if theme_mode == "Light" else "linear-gradient(135deg, #2563eb, #1e40af)"
LIGHT_JD_BUTTON_BG = f"linear-gradient(135deg, #7c3aed, {ACCENT})" if theme_mode == "Light" else "linear-gradient(135deg, #7c3aed, #6d28d9)"

# Calculate theme-specific CSS values
if theme_mode == "Light":
    CARD_SHADOW = "0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1)"
    CARD_BORDER = "1px solid #d1d5db"
    CARD_BACKDROP = "backdrop-filter: none;"
    LOGO_GRADIENT = f"linear-gradient(135deg, {ACCENT}, #1e40af)"
    LOGO_SHADOW = "0 4px 16px rgba(37, 99, 235, 0.3)"
    RESUME_BUTTON_SHADOW = "0 4px 12px rgba(37, 99, 235, 0.3)"
    RESUME_BUTTON_SHADOW_HOVER = "0 6px 20px rgba(37, 99, 235, 0.4)"
    JD_BUTTON_SHADOW = "0 4px 12px rgba(124, 58, 237, 0.3)"
    JD_BUTTON_SHADOW_HOVER = "0 6px 20px rgba(124, 58, 237, 0.4)"
    TEXTAREA_BORDER = "1px solid #9ca3af"
    TEXTAREA_BG = "#f9fafb"
    TEXTAREA_SHADOW = "0 1px 3px rgba(0, 0, 0, 0.1) inset"
    TEXTAREA_FOCUS_SHADOW = f"0 0 0 3px {ACCENT}33"
    EXTRA_STYLES = ""
else:
    CARD_SHADOW = "0 10px 30px rgba(11,43,43,0.06)"
    CARD_BORDER = "1px solid rgba(14,165,164,0.06)"
    CARD_BACKDROP = "backdrop-filter: blur(6px);"
    LOGO_GRADIENT = "linear-gradient(135deg,#06b6d4,#3b82f6)"
    LOGO_SHADOW = "0 8px 24px rgba(14,165,164,0.12)"
    RESUME_BUTTON_SHADOW = "0 8px 18px rgba(6,95,70,0.08)"
    RESUME_BUTTON_SHADOW_HOVER = "0 12px 28px rgba(6,95,70,0.12)"
    JD_BUTTON_SHADOW = "0 8px 18px rgba(124,58,237,0.08)"
    JD_BUTTON_SHADOW_HOVER = "0 12px 28px rgba(124,58,237,0.12)"
    TEXTAREA_BORDER = "1px solid rgba(51, 65, 85, 0.3)"
    TEXTAREA_BG = "rgba(30, 41, 59, 0.4)"
    TEXTAREA_SHADOW = "0 6px 18px rgba(11,43,43,0.04) inset"
    TEXTAREA_FOCUS_SHADOW = "0 0 0 3px rgba(14,165,164,0.1)"
    EXTRA_STYLES = ""

css = f"""
<style>
:root {{ 
  --accent: {ACCENT}; 
  --card-shadow: {CARD_SHADOW};
}}
/* App shell - override Streamlit defaults */
.stApp {{
  background: {BODY_BG} !important;
  color: {TEXT_COLOR} !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif !important;
  transition: background 300ms ease, color 200ms ease;
  padding-bottom:24px;
  
}}

/* Override Streamlit's sidebar - ensure sidebar uses our SIDEBAR_BG */
section[data-testid="stSidebar"] {{
  background: {SIDEBAR_BG} !important;
  border-right: {'-5px solid #9ca3af' if theme_mode == 'Light' else 'none'} !important;
  box-shadow: {'-4px 0 16px rgba(0, 0, 0, 0.06)' if theme_mode == 'Light' else 'none'} !important;
  padding: 0px !important;
  left: 30 !important;
}}


section[data-testid="stSidebar"] .stButton button {{
  width:100% !important;
  border-radius:10px !important;
}}
/* small tweaks for sidebar text contrast */
section[data-testid="stSidebar"] * {{
  color: {TEXT_COLOR} !important;
}}

/* Use accent color for highlights */
a, .stText a, .stMarkdown a {{
  color: var(--accent) !important;
}}

/* Keep the rest of your existing styles (textarea, cards, buttons...) */
{EXTRA_STYLES}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -------------------------
# Parsing utilities
# -------------------------
def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    text = []
    try:
        reader = PdfReader(file_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    except Exception as e:
        st.warning(f"PDF parsing issue: {e}")
    return "\n".join(text)


def extract_text_from_docx(file_stream: io.BytesIO) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
            tmp.write(file_stream.read())
            tmp.flush()
            text = docx2txt.process(tmp.name) or ""
            return text
    except Exception as e:
        st.warning(f"DOCX parsing issue: {e}")
        return ""


def extract_text_from_txt(file_stream: io.BytesIO) -> str:
    try:
        raw = file_stream.read()
        if isinstance(raw, bytes):
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1", errors="ignore")
        else:
            text = str(raw)
        return text
    except Exception as e:
        st.warning(f"TXT parsing issue: {e}")
        return ""


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = "".join(ch for ch in text if (31 < ord(ch) < 127) or ch in ("\n", "\t"))
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[-=]{3,}", "\n", text)
    text = re.sub(r"\n\s*\n{1,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def parse_uploaded_file(uploaded_file) -> Tuple[str, str]:
    if uploaded_file is None:
        return ("", "")
    name = uploaded_file.name
    file_bytes = io.BytesIO(uploaded_file.getvalue())
    lower = name.lower()
    raw = ""
    if lower.endswith(".pdf"):
        raw = extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx") or lower.endswith(".doc"):
        file_bytes.seek(0)
        raw = extract_text_from_docx(file_bytes)
    elif lower.endswith(".txt"):
        file_bytes.seek(0)
        raw = extract_text_from_txt(file_bytes)
    else:
        st.warning(f"Unsupported file type: {name}")
    return (name, clean_text(raw))

# -------------------------
# Skill extraction (unchanged logic but uses custom skills)
# -------------------------
DEFAULT_SKILLS = [
    "python","java","c++","c#","javascript","typescript","react","node","django","flask",
    "sql","nosql","postgres","mongodb","aws","azure","gcp","docker","kubernetes",
    "pandas","numpy","tensorflow","pytorch","scikit-learn","nlp","spark","hadoop",
    "html","css","rest","graphql","git","linux","bash","terraform"
]

_spacy_nlp = None
_spacy_matcher = None
if SPACY_AVAILABLE:
    try:
        _spacy_nlp = spacy.load("en_core_web_sm")
    except Exception:
        _spacy_nlp = None
    if _spacy_nlp:
        _spacy_matcher = PhraseMatcher(_spacy_nlp.vocab, attr="LOWER")
        patterns = [_spacy_nlp.make_doc(s) for s in DEFAULT_SKILLS]
        _spacy_matcher.add("SKILLS", patterns)


def extract_skills(text: str, candidates: List[str]=None) -> List[str]:
    # allow merging default + custom skills from session_state
    if candidates is None:
        candidates = DEFAULT_SKILLS + st.session_state.get("custom_skills", [])
    found = set()
    if not text:
        return []
    if _spacy_matcher and _spacy_nlp:
        doc = _spacy_nlp(text)
        matches = _spacy_matcher(doc)
        for _, start, end in matches:
            found.add(doc[start:end].text.strip().lower())
        # naive fallback: also check custom skills (PhraseMatcher may not have them)
        lower = text.lower()
        for skill in st.session_state.get("custom_skills", []):
            if re.search(r"\b" + re.escape(skill.lower()) + r"\b", lower):
                found.add(skill.lower())
        return sorted(found)
    lower = text.lower()
    for skill in candidates:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, lower):
            found.add(skill)
    return sorted(found)

# -------------------------
# PDF helpers
# -------------------------
def create_pdf_bytes_reportlab(title: str, body: str) -> bytes:
    """Generate a simple PDF with title and body using reportlab. Returns bytes."""
    buffer = io.BytesIO()
    page_w, page_h = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin = 20 * mm
    text_w = page_w - 2 * margin
    y = page_h - margin

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title)
    y -= 12 * mm

    # Body text: wrap manually
    c.setFont("Helvetica", 10)
    lines = []
    for paragraph in body.split("\n"):
        # simple wrapping
        words = paragraph.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 10) < (text_w - 10):
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
        lines.append("")  # paragraph gap

    for line in lines:
        if y < margin + 10 * mm:
            c.showPage()
            y = page_h - margin
            c.setFont("Helvetica", 10)
        c.drawString(margin, y, line)
        y -= 4.8 * mm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def create_pdf_bytes_combined(report_items: List[Tuple[str, str]]) -> bytes:
    """Create PDF containing multiple titled sections (reportlab)."""
    if not _REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab not available")
    buffer = io.BytesIO()
    page_w, page_h = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin = 20 * mm
    text_w = page_w - 2 * margin
    y = page_h - margin

    for title, body in report_items:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, title)
        y -= 10 * mm
        c.setFont("Helvetica", 10)
        lines = []
        for paragraph in body.split("\n"):
            words = paragraph.split()
            line = ""
            for w in words:
                test = (line + " " + w).strip()
                if c.stringWidth(test, "Helvetica", 10) < (text_w - 10):
                    line = test
                else:
                    lines.append(line)
                    line = w
            lines.append(line)
            lines.append("")
        for line in lines:
            if y < margin + 10 * mm:
                c.showPage()
                y = page_h - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, line)
            y -= 4.8 * mm
        # section gap
        y -= 8 * mm
        if y < margin + 20 * mm:
            c.showPage()
            y = page_h - margin
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def pdf_bytes_or_fallback(title: str, body: str) -> Tuple[bytes, str]:
    """
    Returns (file_bytes, mime). If reportlab available returns PDF bytes and 'application/pdf'.
    Otherwise returns plain text bytes and 'text/plain' as fallback.
    """
    if _REPORTLAB_AVAILABLE:
        try:
            b = create_pdf_bytes_reportlab(title, body)
            return b, "application/pdf"
        except Exception as e:
            st.warning(f"PDF generation failed: {e}. Falling back to text.")
    # fallback
    fallback = body.encode("utf-8")
    return fallback, "text/plain"

# -------------------------
# Main UI: hero
# -------------------------
st.markdown(
    f"""
    <div style='text-align:center;margin-top:-40px;margin-bottom:70px'>
      <div style='display:inline-flex;align-items:center;gap:12px'>
        <div style='width:45px;height:45px;margin:0 auto;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;
                        background:linear-gradient(135deg,#06b6d4,#3b82f6);color:#fff;
                        font-weight:800;box-shadow:0 6px 18px rgba(0,0,0,0.08);'>SG</div>
        <h1 style='font-size:40px;margin:0;font-weight:800;display:inline-block;vertical-align:middle;color:{TEXT_COLOR}'>AI Skill Gap Analyzer</h1>
      </div>
      <div style='font-size:17px;color:{MUTED};margin-top:2px'>Instantly compare resumes to job descriptions — highlight missing skills & export results</div>
    </div>
    """, unsafe_allow_html=True
)

# Ensure session state keys
if "resume_manual" not in st.session_state:
    st.session_state["resume_manual"] = ""
if "jd_manual" not in st.session_state:
    st.session_state["jd_manual"] = ""

# Two columns for resume/jd
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Resume")
    resume_file = st.file_uploader("Upload Resume (PDF / DOCX / TXT)", type=["pdf", "docx", "doc", "txt"], key="resume_file")
    st.markdown("OR paste resume text below:")
    resume_manual = st.text_area("Paste resume plain text", value=st.session_state.get("resume_manual", ""), height=180, key="resume_manual_area")

with col2:
    st.subheader("Job Description")
    jd_file = st.file_uploader("Upload Job Description (PDF / DOCX / TXT)", type=["pdf", "docx", "doc", "txt"], key="jd_file")
    st.markdown("OR paste JD text below:")
    jd_manual = st.text_area("Paste job description plain text", value=st.session_state.get("jd_manual", ""), height=180, key="jd_manual_area")

# update sidebar file-name placeholders (so sidebar shows file info)
if resume_file is not None:
    st.session_state["resume_file_name"] = resume_file.name
else:
    st.session_state["resume_file_name"] = st.session_state.get("resume_file_name", "")

if jd_file is not None:
    st.session_state["jd_file_name"] = jd_file.name
else:
    st.session_state["jd_file_name"] = st.session_state.get("jd_file_name", "")

# small spacer
st.markdown("<div class='small-space'></div>", unsafe_allow_html=True)

# Parse controls (make parse button reliable)
col_parse1, col_parse2, col_parse3 = st.columns([1, 1, 2])
with col_parse1:
    # explicit key ensures stable identity
    parse_btn = st.button("Parse & Clean", use_container_width=True, key="parse_btn")
with col_parse2:
    auto_hint = st.checkbox("Show preview automatically", value=False, help="Enable to auto-preview content in the panels.")
# col_parse3 intentionally empty

# Populate sample templates once when selected
if sample != "None":
    if sample == "Software Engineer (JD)":
        st.session_state["jd_manual"] = "We are looking for a Software Engineer with 3+ years experience in Python, Django, REST APIs, AWS, Docker, and PostgreSQL..."
    elif sample == "Data Scientist (JD)":
        st.session_state["jd_manual"] = "Looking for a Data Scientist skilled in Python, pandas, numpy, scikit-learn, TensorFlow, SQL, and AWS S3..."
    elif sample == "Sample Resume":
        st.session_state["resume_manual"] = "Karthik — Software Engineer\nSkills: Python, Django, REST, PostgreSQL, Docker, AWS.\nExperience: Built microservices in Python..."

resume_manual = st.session_state.get("resume_manual", "")
jd_manual = st.session_state.get("jd_manual", "")

# Parse trigger condition
should_parse = parse_btn or (auto_parse and (resume_file is not None or jd_file is not None or resume_manual.strip() or jd_manual.strip()))

resume_name = ""
jd_name = ""
resume_text = ""
jd_text = ""

if should_parse:
    # Resume parsing
    if resume_file is not None:
        resume_name, resume_text = parse_uploaded_file(resume_file)
    else:
        resume_name = "pasted_resume.txt" if resume_manual.strip() else ""
        resume_text = clean_text(resume_manual)
    # JD parsing
    if jd_file is not None:
        jd_name, jd_text = parse_uploaded_file(jd_file)
    else:
        jd_name = "pasted_jd.txt" if jd_manual.strip() else ""
        jd_text = clean_text(jd_manual)

    # update session state
    st.session_state["resume_manual"] = resume_text
    st.session_state["jd_manual"] = jd_text

    # update app stats (simple increments)
    st.session_state["app_stats"]["files_parsed"] += 1
    # update skill count estimate
    st.session_state["app_stats"]["skills_detected"] = len(set(extract_skills(resume_text + "\n" + jd_text)))

# -------------------------
# Preview panels
# -------------------------
# Section separator before preview panels
st.markdown("<hr class='section-separator'>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
preview_left, preview_right = st.columns([1, 1])

def render_stats_block(text: str):
    words = len(text.split()) if text else 0
    chars = len(text)
    lines = text.count("\n") + 1 if text else 0
    uniq_words = len(set(text.lower().split())) if text else 0
    return words, chars, lines, uniq_words

# Resume preview (left)
with preview_left:
    st.markdown("### Resume Preview")
    resume_text = st.session_state.get("resume_manual", "")
    if resume_text:
        r_words, r_chars, r_lines, r_uniq = render_stats_block(resume_text)
        st.markdown(f"<div><span style='font-weight:700;font-size:18px'>{r_words}</span> words &nbsp; <span class='small muted'>|</span> &nbsp; <span style='font-weight:700;font-size:18px'>{r_chars}</span> chars</div>", unsafe_allow_html=True)
        percent = min(100, int(r_words / 800 * 100))
        st.markdown("<div style='height:8px;background:rgba(0,0,0,0.06);border-radius:4px;overflow:hidden;margin-top:8px;margin-bottom:10px'><div style='height:100%;background:linear-gradient(90deg,#34d399,#10b981);width:"+str(percent)+"%'></div></div>", unsafe_allow_html=True)
        st.text_area("Resume (cleaned)", value=resume_text, height=320, key="preview_resume_area")

        # Buttons row: Copy (green), Download .txt, Download as PDF (green)
        cols = st.columns([1, 1, 1])
        with cols[0]:
            safe_text = json.dumps(resume_text)
            # green copy button (resume)
            html = (
                "<button id='btn-resume' class='resume-copy'>Copy Resume</button>"
                "<script>"
                "document.getElementById('btn-resume').addEventListener('click', async () => {"
                "try { await navigator.clipboard.writeText(" + safe_text + "); document.getElementById('btn-resume').innerText = 'Copied ✓'; setTimeout(()=>{ document.getElementById('btn-resume').innerText = 'Copy Resume'; }, 1400);"
                "} catch(e) { alert('Copy failed — please copy manually.'); }"
                "});"
                "</script>"
            )
            components.html(html, height=48)
        with cols[1]:
            st.download_button("Download .txt", data=resume_text, file_name=(resume_name or "resume") + ".txt", mime="text/plain")
        with cols[2]:
            # Download as PDF (Resume)
            pdf_bytes, mime = pdf_bytes_or_fallback("Resume — " + (resume_name or "resume"), resume_text)
            # if it's text fallback, change filename extension accordingly
            fn = (resume_name or "resume")
            if mime == "application/pdf":
                fname = fn.rsplit(".", 1)[0] + ".pdf"
            else:
                fname = fn.rsplit(".", 1)[0] + ".txt"
            st.download_button("Download as PDF", data=pdf_bytes, file_name=fname, mime=mime)

           # small spacer
        st.markdown("<div class='small-space'></div>", unsafe_allow_html=True)

        # small spacer
        st.markdown("<div class='small-space'></div>", unsafe_allow_html=True)
 

        if show_skill_highlights:
            skills_found = extract_skills(resume_text)
            st.markdown("Skill Highlights: " + (", ".join(skills_found) if skills_found else "No known skills found (try adding custom keywords)"))
    else:
        st.info("No resume content yet. Upload or paste text and click 'Parse & Clean' (or enable Auto-parse).")

# JD preview (right)
with preview_right:
    st.markdown("### Job Description Preview")
    jd_text = st.session_state.get("jd_manual", "")
    if jd_text:
        j_words, j_chars, j_lines, j_uniq = render_stats_block(jd_text)
        st.markdown(f"<div><span style='font-weight:700;font-size:18px'>{j_words}</span> words &nbsp; <span class='small muted'>|</span> &nbsp; <span style='font-weight:700;font-size:18px'>{j_chars}</span> chars</div>", unsafe_allow_html=True)
        percent_j = min(100, int(j_words / 1200 * 100))
        st.markdown("<div style='height:8px;background:rgba(0,0,0,0.06);border-radius:4px;overflow:hidden;margin-top:8px;margin-bottom:10px'><div style='height:100%;background:linear-gradient(90deg,#c084fc,#7c3aed);width:"+str(percent_j)+"%'></div></div>", unsafe_allow_html=True)
        st.text_area("Job Description (cleaned)", value=jd_text, height=320, key="preview_jd_area")

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            safe = json.dumps(jd_text)
            # purple copy button (jd)
            html = (
                "<button id='btn-jd' class='jd-copy'>Copy JD</button>"
                "<script>"
                "document.getElementById('btn-jd').addEventListener('click', async () => {"
                "try { await navigator.clipboard.writeText(" + safe + "); document.getElementById('btn-jd').innerText = 'Copied ✓'; setTimeout(()=>{ document.getElementById('btn-jd').innerText = 'Copy JD'; }, 1400);"
                "} catch(e) { alert('Copy failed — please copy manually.'); }"
                "});"
                "</script>"
            )
            components.html(html, height=48)
        with c2:
            st.download_button("Download .txt", data=jd_text, file_name=(jd_name or "job_description") + ".txt", mime="text/plain")
        with c3:
            # Download as PDF (JD)
            pdf_bytes, mime = pdf_bytes_or_fallback("Job Description — " + (jd_name or "job_description"), jd_text)
            fn = (jd_name or "job_description")
            if mime == "application/pdf":
                fname = fn.rsplit(".", 1)[0] + ".pdf"
            else:
                fname = fn.rsplit(".", 1)[0] + ".txt"
            st.download_button("Download as PDF", data=pdf_bytes, file_name=fname, mime=mime)
          

          # small spacer
        st.markdown("<div class='small-space'></div>", unsafe_allow_html=True)

        # small spacer
        st.markdown("<div class='small-space'></div>", unsafe_allow_html=True)
        
        if show_skill_highlights:
            skills_found_j = extract_skills(jd_text)
            st.markdown("JD Skill Highlights: " + (", ".join(skills_found_j) if skills_found_j else "No known skills found in JD"))
    else:
        st.info("No JD content yet. Upload or paste text and click 'Parse & Clean' (or enable Auto-parse).")

# -------------------------
# Combined Export: single PDF for both parsed data
# -------------------------
# Section separator before combined export section
st.markdown("<hr class='section-separator'>", unsafe_allow_html=True)
if st.session_state.get("resume_manual", "") or st.session_state.get("jd_manual", ""):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Combined Export & Quick Actions")
    records = []
    if st.session_state.get("resume_manual", ""):
        records.append(("Resume", st.session_state.get("resume_manual", "")))
    if st.session_state.get("jd_manual", ""):
        records.append(("Job Description", st.session_state.get("jd_manual", "")))

    # Build combined PDF (reportlab) if available; else fallback to combined text
    if _REPORTLAB_AVAILABLE:
        try:
            combined_pdf = create_pdf_bytes_combined(records)
            st.download_button("Download combined PDF (Resume + JD)", data=combined_pdf, file_name="parsed_documents_combined.pdf", mime="application/pdf")
        except Exception as e:
            st.warning(f"Combined PDF generation failed: {e}. Offering text fallback.")
            combined_text = "\n\n".join([f"=== {t} ===\n\n{b}" for t, b in records])
            st.download_button("Download combined (text)", data=combined_text, file_name="parsed_documents_combined.txt", mime="text/plain")
    else:
        # fallback: return combined text
        combined_text = "\n\n".join([f"=== {t} ===\n\n{b}" for t, b in records])
        st.download_button("Download combined (text)", data=combined_text, file_name="parsed_documents_combined.txt", mime="text/plain")

    # Quick overlap as before (unchanged)
    if show_skill_highlights and len(records) == 2:
        r_skills = set(extract_skills(records[0][1]))
        j_skills = set(extract_skills(records[1][1]))
        overlap = r_skills.intersection(j_skills)
        overlap_pct = int(len(overlap) / (len(j_skills) if j_skills else 1) * 100) if j_skills else 0
        st.markdown(f"Quick skill overlap: {len(overlap)} shared skills — <span style='color:var(--accent);'>{overlap_pct}% of JD skills matched by resume</span>", unsafe_allow_html=True)
        if overlap:
            st.markdown("Shared skills: " + ", ".join(sorted(overlap)))
    
    # Section separator after combined export section
    st.markdown("<hr class='section-separator'>", unsafe_allow_html=True)

# -------------------------
# Footer (two-column: left app title, right last-updated)
# -------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style='width:100%; display:flex; justify-content:space-between; align-items:center;'>
        <div style='text-align:left;font-size:20px;color:{TEXT_COLOR};font-weight:600;'>
            <em>AI Skill Gap Analyzer — Milestone 1</em>
        </div>
        <div style='text-align:right;font-size:18px;color:{MUTED};'>
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<div style='text-align:left;font-size:16px;color:{MUTED};'>Version: {st.session_state.get('app_version','1.0.0')} • Developed by Balu Karthik</div>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)
# End of file