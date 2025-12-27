import streamlit as st
import io
import re
import time
import json
from collections import Counter
from datetime import datetime
from typing import Tuple, List
import textwrap

import components as ui_components

# -------------------------------------------------------
# DATA: Sample JDs for Auto-Fill
# -------------------------------------------------------
SAMPLE_ROLES = {
    "Administrative Assistant": "Responsibilities:\n- Manage executive calendars and schedule meetings.\n- Handle travel arrangements and expense reports.\n- Serve as the primary point of contact for internal/external communications.\n- Maintain filing systems and office supplies.\n\nRequirements:\n- Proven experience as an administrative assistant.\n- Proficiency in MS Office (Outlook, Word, Excel).\n- Excellent time management and organizational skills.\n- High school diploma; specialized certification is a plus.",
    "Backend Developer (Python/Node)": "Responsibilities:\n- Design and build efficient, scalable server-side applications.\n- Develop RESTful APIs and integrate with frontend components.\n- Optimize database queries and manage migrations (SQL/NoSQL).\n- Collaborate with frontend developers to ship features.\n\nRequirements:\n- Strong proficiency in Python (Django/Flask) or Node.js.\n- Understanding of databases (PostgreSQL, MongoDB).\n- Knowledge of cloud platforms (AWS/Azure) and Docker.\n- Experience with Unit Testing and CI/CD pipelines.",
    "Blockchain Developer": "Responsibilities:\n- Research and design blockchain technologies.\n- Develop smart contracts using Solidity or Rust.\n- Implement secure blockchain protocols and architecture.\n- Maintain and extend current client-side applications.\n\nRequirements:\n- Strong background in software development and cryptography.\n- Experience with Ethereum/Web3.js or other blockchain frameworks.\n- Knowledge of P2P networks and consensus algorithms.\n- Proficiency in C++, Java, or Go is a plus.",
    "Business Analyst": "Responsibilities:\n- Analyze business processes and identify areas for improvement.\n- Gather and document requirements from stakeholders.\n- Translate business needs into technical specifications.\n- Create data visualizations and reports to support decision making.\n\nRequirements:\n- Degree in Business, Finance, or IT.\n- Strong analytical and problem-solving skills.\n- Proficiency in SQL, Excel, and BI tools (Tableau/PowerBI).\n- Excellent communication skills.",
    "Cloud Architect (AWS/Azure)": "Responsibilities:\n- Design and deploy scalable, highly available, and fault-tolerant systems.\n- Migrate existing on-premise applications to the cloud.\n- Manage cloud capabilities/security and optimize costs.\n- Provide guidance to development teams on cloud best practices.\n\nRequirements:\n- In-depth knowledge of AWS or Azure architecture.\n- Experience with Infrastructure as Code (Terraform/CloudFormation).\n- Understanding of networking, security, and compliance.\n- Relevant certifications (e.g., AWS Solutions Architect).",
    "Content Writer": "Responsibilities:\n- Research industry-related topics and generate ideas.\n- Write clear, marketing copy to promote our products/services.\n- Proofread and edit blog posts before publication.\n- Coordinate with marketing privacy and design teams to illustrate articles.\n\nRequirements:\n- Proven work experience as a Content Writer or Copywriter.\n- Portfolio of published articles.\n- Excellent writing and editing skills in English.\n- Hands-on experience with Content Management Systems (e.g. WordPress).",
    "Customer Success Manager": "Responsibilities:\n- Serve as the primary contact for onboarding new clients.\n- Build long-term relationships with customers and ensure satisfaction.\n- Identify up-sell opportunities and reduce churn.\n- Troubleshoot technical issues and coordinate with support.\n\nRequirements:\n- Experience in Customer Success or Account Management.\n- Strong communication and negotiation skills.\n- Ability to explain complex topics clearly.\n- Experience with CRM software (Salesforce/HubSpot).",
    "Data Scientist": "Responsibilities:\n- Preprocess and analyze large datasets to extract insights.\n- Build and deploy predictive models using Machine Learning algorithms.\n- Visualize data findings for non-technical stakeholders.\n- Collaborate with engineering to productionalize models.\n\nRequirements:\n- Proficiency in Python (Pandas, Scikit-learn) and SQL.\n- Strong background in Statistics and Mathematics.\n- Experience with deep learning frameworks (TensorFlow/PyTorch) is a plus.\n- Master's or PhD in written field preferred.",
    "Digital Marketing Specialist": "Responsibilities:\n- Design and oversee all aspects of digital marketing department.\n- Manage SEO/SEM, marketing database, email, and social media campaigns.\n- Identify trends and optimize spend and performance based on insights.\n- Brainstorm new and creative growth strategies.\n\nRequirements:\n- Proven working experience in digital marketing.\n- Demonstrable experience leading and managing SEO/SEM, marketing database, email, social media and/or display advertising campaigns.\n- Highly creative with experience in identifying target audiences.",
    "Frontend Developer (React/Vue)": "Responsibilities:\n- Develop new user-facing features using React.js or Vue.js.\n- Build reusable code and libraries for future use.\n- Ensure the technical feasibility of UI/UX designs.\n- Optimize application for maximum speed and scalability.\n\nRequirements:\n- Strong proficiency in JavaScript, HTML5, and CSS3.\n- In-depth understanding of React.js/Vue.js and their core principles.\n- Experience with state management (Redux/Vuex).\n- Familiarity with RESTful APIs.",
    "Full Stack Developer": "Responsibilities:\n- Work across the full stack, building highly scalable distributed solutions.\n- Enable analytics that drive business decisions and improve availability.\n- Construct and maintain robust APIs.\n- Work in an Agile environment to deliver high-quality software.\n\nRequirements:\n- Proficiency in frontend technologies (React/Angular) and backend (Node/Python/Java).\n- Experience with database design (SQL/NoSQL).\n- Familiarity with cloud services (AWS/GCP).\n- Strong problem-solving skills.",
    "Graphic Designer": "Responsibilities:\n- Conceptualize visuals based on requirements.\n- Prepare rough drafts and present ideas.\n- Develop illustrations, logos and other designs using software.\n- Ensure final graphics and layouts are visually appealing.\n\nRequirements:\n- Proven graphic designing experience.\n- A strong portfolio of illustrations or other graphics.\n- Familiarity with design software (Adobe Creative Suite).\n- A keen eye for aesthetics and details.",
    "Human Resources Manager": "Responsibilities:\n- Develop and implement HR strategies and initiatives.\n- Bridge management and employee relations.\n- Manage the recruitment and selection process.\n- Oversee and manage a performance appraisal system.\n\nRequirements:\n- Proven working experience as HR Manager or other HR Executive.\n- People oriented and results driven.\n- Knowledge of HR systems and databases.\n- Excellent active listening, negotiation and presentation skills.",
    "Mobile App Developer (Flutter/iOS)": "Responsibilities:\n- Support the entire application lifecycle (concept, design, test, release, support).\n- Produce fully functional mobile applications writing clean code.\n- Gather specific requirements and suggest solutions.\n- Troubleshoot and debug to optimize performance.\n\nRequirements:\n- Proven work experience as a Mobile developer.\n- Demonstrable portfolio of released applications on the App store or the Android market.\n- Experience with Flutter, Swift, or Kotlin.\n- Familiarity with OOP design principles.",
    "Product Manager": "Responsibilities:\n- Gain a deep understanding of customer experience, identify and fill product gaps.\n- Scope and prioritize activities based on business and customer impact.\n- Work closely with engineering teams to deliver with quick time-to-market.\n- Drive product launches including working with public relations team.\n\nRequirements:\n- Proven work experience in product management.\n- Proven track record of managing all aspects of a successful product throughout its lifecycle.\n- Solid technical background with understanding of software development.\n- Skilled at working effectively with cross functional teams.",
    "Project Manager": "Responsibilities:\n- Coordinate internal resources and third parties/vendors for the flawless execution of projects.\n- Ensure that all projects are delivered on-time, within scope and within budget.\n- Assist in the definition of project scope and objectives.\n- Rigid detailed project plans to monitor and track progress.\n\nRequirements:\n- Proven working experience in project management.\n- Excellent client-facing and internal communication skills.\n- Solid organizational skills including attention to detail and multi-tasking skills.\n- PMP / PRINCE II certification is a plus.",
    "Sales Representative": "Responsibilities:\n- Present, promote and sell products/services using solid arguments to existing and prospective customers.\n- Perform cost-benefit and needs analysis of existing/potential customers.\n- Establish, develop and maintain positive business and customer relationships.\n- Expedite the resolution of customer problems and complaints.\n\nRequirements:\n- Proven work experience as a Sales Representative.\n- Excellent knowledge of MS Office.\n- Highly motivated and target driven with a proven track record in sales.\n- Excellent selling, negotiation and communication skills.",
    "Software Engineer": "Responsibilities:\n- Develop high-quality software design and architecture.\n- Identify, prioritize and execute tasks in the software development life cycle.\n- Develop tools and applications by producing clean, efficient code.\n- Automate tasks through appropriate tools and scripting.\n\nRequirements:\n- Proven experience as a Software Engineer.\n- Extensive experience in software development, scripting and project management.\n- Proficiency in selected programming languages (e.g. Java, C++).\n- In-depth knowledge of relational databases (e.g. PostgreSQL, MySQL).",
}

try:
    from pypdf import PdfReader
    import docx2txt
except ImportError:
    pass 

# -------------------------------------------------------
# PERFORMANCE: Lazy Load Heavy Libraries
# -------------------------------------------------------
try:
    from milestone2 import load_nlp, extract_skills
except ImportError:
   
    def load_nlp():
        import spacy
        try: return spacy.load("en_core_web_sm")
        except: 
            # Fallback
            from spacy.lang.en import English
            return English()

    def extract_skills(text):
        return [], []

@st.cache_resource(show_spinner="Loading OCR Model...")
def get_ocr_reader():
    """Lazy load EasyOCR reader."""
    try:
        import easyocr
        return easyocr.Reader(['en'], gpu=False, verbose=False)
    except ImportError:
        return None

# -------------------------------------------------------
# UTILITIES & ANALYTICS
# -------------------------------------------------------
def calculate_reading_time(text: str) -> str:
    words = len(text.split())
    minutes = words / 200
    if minutes < 1:
        return "< 1 min"
    return f"~{int(minutes)} min"

@st.cache_data
def analyze_resume_health(text: str) -> dict:
    """Performs a basic health check on the resume text."""
    score = 0
    checks = []
    
    # 1. Word Count Check
    words = len(text.split())
    if 400 <= words <= 1200:
        score += 25
        checks.append("✅ Optimal Word Count")
    elif words < 400:
        score += 10
        checks.append("⚠️ Word count low (< 400)")
    else:
        score += 15
        checks.append("⚠️ Word count high (> 1200)")
        
    # 2. Section Detection
    lower_text = text.lower()
    sections = ["experience", "education", "skills", "projects", "summary"]
    found_sections = [s for s in sections if s in lower_text]
    score += (len(found_sections) * 10)  # Max 50
    if len(found_sections) == 5:
        checks.append("✅ All Key Sections Detected")
    else:
        missing = [s.title() for s in sections if s not in lower_text]
        checks.append(f"⚠️ Missing Sections: {', '.join(missing)}")
        
    # 3. Contact Info (Basic Regex)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    
    has_email = re.search(email_pattern, text)
    has_phone = re.search(phone_pattern, text)
    
    if has_email:
        score += 15
    if has_phone:
        score += 10
    
    if has_email and has_phone:
        checks.append("✅ Contact Info Detected")
    elif not has_email:
        checks.append("❌ No Email Found")
        
    return {"score": min(100, score), "checks": checks}

@st.cache_data
def analyze_jd_health(text: str) -> dict:
    """Analyzes Job Description clarity and completeness."""
    score = 0
    checks = []
    lower_text = text.lower()
    
    # 1. Length Check
    words = len(text.split())
    if 200 <= words <= 1500:
        score += 30
        checks.append("✅ Good JD Length")
    else:
        score += 10
        checks.append("⚠️ JD Length Irregular")

    # 2. Key Terms
    terms = ["responsibilities", "qualifications", "requirements", "benefits", "about"]
    found = [t for t in terms if t in lower_text]
    score += (len(found) * 10)  # Max 50
    
    if len(found) >= 4:
        checks.append("✅ Comprehensive Structure")
    else:
        checks.append("⚠️ Missing Structural Elements")
        
    # 3. Jargon/Clarity (Simple proxy)
    if "salary" in lower_text or "compensation" in lower_text:
        score += 20
        checks.append("✅ Compensation Mentioned")
    else:
        checks.append("⚠️ No Salary Info")
        
    return {"score": min(100, score), "checks": checks}

@st.cache_data
def calculate_pre_match(resume_text: str, jd_text: str) -> int:
    """Calculates a quick Jaccard similarity score for pre-screening."""
    r_tokens = set(re.findall(r'\w+', resume_text.lower()))
    j_tokens = set(re.findall(r'\w+', jd_text.lower()))
    
    # Filter stopwords
    stopwords = {
        "and", "the", "to", "of", "in", "a", "with", "for", "on", "as", "an",
        "is", "that", "by", "it", "or", "at", "from", "be", "this", "are",
        "work", "experience", "skills", "education", "responsibilities", "requirements"
    }
    r_tokens = {w for w in r_tokens if w not in stopwords and len(w) > 3}
    j_tokens = {w for w in j_tokens if w not in stopwords and len(w) > 3}
    
    if not r_tokens or not j_tokens:
        return 0
    
    intersection = len(r_tokens.intersection(j_tokens))
    union = len(r_tokens.union(j_tokens))
    
    return int((intersection / union) * 100 * 3)  # Boosted factor for display

@st.cache_data
def get_top_keywords(text: str, n=10) -> List[Tuple[str, int]]:
    """Simple frequency analysis for 'Quick Glance'."""
    stopwords = {
        "and", "the", "to", "of", "in", "a", "with", "for", "on", "as", "an",
        "is", "that", "by", "it", "or", "at", "from", "be", "this", "are",
        "work", "experience", "skills", "education", "will", "have", "your"
    }
    words = re.findall(r'\w+', text.lower())
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    return Counter(filtered).most_common(n)

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@st.cache_data(show_spinner=False)
def _parse_bytes(file_bytes_data, file_name, max_pages=5):
    """
    Cached worker for file parsing. 
    Accepts bytes instead of file object to allow Streamlit caching.
    """
    import io
    try:
        from pypdf import PdfReader
        import docx2txt
    except ImportError:
        pass

    file_obj = io.BytesIO(file_bytes_data)
    name = file_name.lower()
    
    if name.endswith(".pdf"):
        try:
            reader = PdfReader(file_obj)
            pages = reader.pages[:min(len(reader.pages), max_pages)]
            text_blocks = []
            
            ocr_model = None # Lazy init
            
            for i, page in enumerate(pages):
                # 1. Standard Extraction
                extracted = page.extract_text() or ""
                # 2. OCR Extraction (if needed)
                if len(extracted.strip()) < 50: 
                    # Optimization: Limit OCR to first 2 pages max
                    if i < 2 and hasattr(page, "images") and len(page.images) > 0:
                        import components
                        # Lazy load OCR only if absolutely needed
                        if ocr_model is None:
                             ocr_model = get_ocr_reader()
                        
                        if ocr_model:
                            ocr_text = []
                            for img in page.images:
                                try:
                                    # detail=0 for faster output
                                    results = ocr_model.readtext(img.data, detail=0, paragraph=True)
                                    ocr_text.extend(results)
                                except:
                                    pass
                            
                            if ocr_text:
                                extracted += "\n" + "\n".join(ocr_text)

                if extracted.strip():
                    text_blocks.append(extracted)
                    
            return "\n".join(text_blocks)

        except Exception as e:
            return ""
            
    elif name.endswith(".docx") or name.endswith(".doc"):
        try:
            return docx2txt.process(file_obj)
        except:
            return ""
    elif name.endswith(".txt"):
        return file_bytes_data.decode("utf-8", errors="ignore")
    return ""

def parse_file(uploaded_file, max_pages=5) -> str:
    """Wrapper that handles the Streamlit file object and calls cached worker."""
    if uploaded_file is None:
        return ""
    
    # Pass bytes to cached function
    return _parse_bytes(uploaded_file.getvalue(), uploaded_file.name, max_pages)
# -------------------------------------------------------
# MAIN APP
# -------------------------------------------------------
def app():
    ui_components.render_navbar()
    ui_components.scroll_to_top(smooth=False, delay_ms=50)

    st.markdown(
        """
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
            margin-top: 100px; 
        }
        .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px; display: flex; align-items: center; justify-content: center; gap: 15px; }
        .hero-sub { font-size: 1.1rem; opacity: 0.9; font-weight: 300; }
        
        .stat-box {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 15px;
            border: var(--card-border);
            text-align: center;
            transition: transform 0.2s;
            box-shadow: var(--card-shadow);
        }
        .stat-box:hover { transform: translateY(-5px); }
        .stat-val { font-size: 1.8rem; font-weight: 800; color: #3B82F6; }
        .stat-lbl { font-size: 0.8rem; color: var(--muted-color); text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Health Score Circle */
        .health-score-circle {
            width: 80px; height: 80px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 10px auto;
            position: relative;
        }
        .health-score-inner {
            width: 65px; height: 65px; border-radius: 50%; background: var(--card-bg);
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 1.2rem; color: var(--text-color);
            position: absolute;
            top: 7.5px; left: 7.5px;
        }
        
        /* Footer Fix */
        .block-container { padding-bottom: 0 !important; }
        .footer-bar {
            width: 100vw;
            margin-left: -50vw;
            margin-right: -50vw;
            position: relative;
            left: 50%;
            right: 50%;
            background: #020617;
            padding: 60px 20px;
            text-align: center;
            border-top: 1px solid #1e293b;
            margin-top: 80px;
        }
        .footer-text {
            font-size: 0.9rem;
            color: #e2e8f0;
            font-weight: 500;
        }
        
        /* Blue Primary Button Styling */
        .stButton button[kind="primary"] {
            background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1.1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.6);
        }
        
        /* Processing Card Styles */
        .processing-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            animation: fadeIn 0.5s ease-out;
        }
        .processing-header {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            color: #e2e8f0;
            margin-bottom: 15px;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 10px;
        }
        .step-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
            color: #94a3b8;
            transition: all 0.3s ease;
        }
        .step-item.active {
            color: #3B82F6;
            font-weight: 600;
        }
        .step-item.done {
            color: #10B981;
        }
        .step-icon {
            width: 20px;
            display: flex;
            justify-content: center;
        }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .spinner-icon {
            animation: spin 1s linear infinite;
            color: #3B82F6;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Logo Animation */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        .logo-icon {
            animation: float 3s ease-in-out infinite;
        }
        
        /* New Feature: Tip Box */
        .tip-box {
            background: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3B82F6;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }

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
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    ui_components.render_stepper(current_step=1)

    # Enhanced SVG Logo
    logo_svg = '<svg width="35" height="35" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon"><defs><linearGradient id="grad4" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#22D3EE" /><stop offset="100%" stop-color="#3B82F6" /></linearGradient><filter id="glow4" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><rect x="10" y="10" width="44" height="44" rx="12" stroke="url(#grad4)" stroke-width="4" fill="none"/><path d="M24 36L30 36L28 46L40 28L34 28L36 18L24 36Z" fill="white" filter="url(#glow4)"/><circle cx="32" cy="8" r="3" fill="#22D3EE"/><circle cx="32" cy="56" r="3" fill="#3B82F6"/><circle cx="8" cy="32" r="3" fill="#22D3EE"/><circle cx="56" cy="32" r="3" fill="#3B82F6"/></svg>'
    
    st.markdown(textwrap.dedent(f"""\
        <div class="hero-section">
            <div class="hero-title">
                {logo_svg}
                <div>Intelligent Document Ingestion</div>
            </div>
            <div class="hero-sub">Upload your Resume and Job Description to unlock AI-powered skill gap insights.</div>
        </div>
    """), unsafe_allow_html=True)
    
    # New Feature: Quick Tip
    st.markdown(
        """
        <div class="tip-box">
            <strong>💡 Pro Tip:</strong> For best results, use PDF resumes with selectable text. Scanned images might not be parsed correctly.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # INPUT AREA (GLASSMORPHISM)
    # -------------------------
    col_left, col_right = st.columns(2)

    # Initialize Session State
    if "resume_manual" not in st.session_state:
        st.session_state["resume_manual"] = ""
    if "jd_manual" not in st.session_state:
        st.session_state["jd_manual"] = ""
    if "resume_filename" not in st.session_state:
        st.session_state["resume_filename"] = ""
    if "jd_filename" not in st.session_state:
        st.session_state["jd_filename"] = ""

    with col_left:
        st.markdown(
            '<div style="font-weight:700; font-size:1.2rem; margin-bottom:10px; color:var(--text-color);">1. Candidate Resume</div>',
            unsafe_allow_html=True,
        )
        tab_r1, tab_r2 = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        with tab_r1:
            resume_file = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx", "txt"],
                key="uploader_resume_m1",
                label_visibility="collapsed",
            )
        with tab_r2:
            resume_paste = st.text_area(
                "Paste Resume",
                height=150,
                placeholder="Paste text here...",
                label_visibility="collapsed",
            )

        # Create New Resume Section (Matching JD Interface)
        st.markdown(textwrap.dedent(f"""\
            <div style="display: flex; align-items: center; gap: 5px; margin: 15px 0 10px 0;">
                <div style="height: 1px; background: #334155; flex-grow: 1;"></div>
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">OR CREATE NEW</div>
                <div style="height: 1px; background: #334155; flex-grow: 1;"></div>
            </div>
            """), unsafe_allow_html=True
        )
        
        if st.button("📝 Launch Resume Builder", key="launch_builder_m1", use_container_width=True):
             st.session_state["nav_page"] = "Resume Builder"
             st.rerun()

    with col_right:
        st.markdown(
            '<div style="font-weight:700; font-size:1.2rem; margin-bottom:10px; color:var(--text-color);">2. Job Description</div>',
            unsafe_allow_html=True,
        )
        tab_j1, tab_j2 = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        with tab_j1:
            jd_file = st.file_uploader(
                "Upload JD",
                type=["pdf", "docx", "txt"],
                key="uploader_jd_m1",
                label_visibility="collapsed",
            )
        # ensure session key exists for the textarea
        if "jd_input_content" not in st.session_state:
            st.session_state["jd_input_content"] = ""

        def update_jd_from_dropdown():
            selected = st.session_state.get("jd_role_dropdown")
            if selected and selected != "Select Role...":
                 st.session_state["jd_input_content"] = SAMPLE_ROLES.get(selected, "")

        with tab_j2:
            jd_paste = st.text_area(
                "Paste JD",
                height=150,
                placeholder="Paste text here or select a role below...",
                label_visibility="collapsed",
                key="jd_input_content" # This binds the text area value to session state
            )

        # Dropdown for Auto-fill
        st.markdown(textwrap.dedent(f"""\
            <div style="display: flex; align-items: center; gap: 5px; margin: 15px 0 10px 0;">
                <div style="height: 1px; background: #334155; flex-grow: 1;"></div>
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">OR AUTO-FILL</div>
                <div style="height: 1px; background: #334155; flex-grow: 1;"></div>
            </div>
            """), unsafe_allow_html=True
        )
        
        role_options = ["Select Role..."] + sorted(list(SAMPLE_ROLES.keys()))
        st.selectbox(
            "Select a Role to Auto-Fill JD",
            role_options,
            key="jd_role_dropdown",
            label_visibility="collapsed",
            on_change=update_jd_from_dropdown
        )

        # Auto-Fill Preview
        if st.session_state.get("jd_role_dropdown") and st.session_state["jd_role_dropdown"] != "Select Role...":
            st.markdown("<div style='margin-top: 10px; font-size: 0.9rem; color: #94a3b8;'>📄 Preview of Selected Role:</div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 8px; border: 1px solid #334155; font-size: 0.85rem; max-height: 250px; overflow-y: auto; white-space: pre-wrap; color: #cbd5e1;">{st.session_state.get('jd_input_content', '')}</div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Tip: You can edit this text in the '✍️ Paste Text' tab above.")

    # -------------------------
    # ACTION BUTTON
    # -------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
    with col_act2:
        process_btn = st.button("✨ Analyze & Process Documents", type="primary", use_container_width=True)

    # Initialize processed state
    if "m1_processed" not in st.session_state:
        st.session_state["m1_processed"] = False

    # -------------------------
    # PROCESSING LOGIC
    # -------------------------
    if process_btn:
        # VALIDATION: Check if inputs exist
        has_resume = resume_file is not None or resume_paste.strip() != ""
        has_jd = jd_file is not None or jd_paste.strip() != ""
        
        if not has_resume or not has_jd:
            st.error("⚠️ Please upload BOTH a Resume and a Job Description before analyzing.")
        else:
            # Custom Animated Status Container
            status_container = st.empty()
            
            def update_status(completed=False):
                
                # If completed, show success
                if completed:
                    html_content = textwrap.dedent("""\
                        <div class="processing-card" style="border-color: #10B981;">
                            <div class="processing-header" style="border-bottom:none; margin-bottom:0;">
                                <div style="color:#10B981; font-size:1.5rem;">✅</div>
                                <div>Documents Processed Successfully!</div>
                            </div>
                        </div>
                    """)
                    status_container.markdown(html_content, unsafe_allow_html=True)
                    return

                # Otherwise show unified processing state
                html_content = textwrap.dedent("""\
                    <div class="processing-card">
                        <div class="processing-header">
                            <div class="spinner-icon">⚙️</div>
                            <div>Processing Engine Started...</div>
                        </div>
                        <div class="step-item active">
                            <div class="step-icon">🔄</div>
                            <div class="step-text">Ingesting & Analyzing Documents...</div>
                        </div>
                    </div>
                """)
                status_container.markdown(html_content, unsafe_allow_html=True)

            # 1. Start Processing UI
            update_status(completed=False)
            
            # 2. Parse Files (Optimized max_pages for speed)
            r_text = ""
            r_name = "Manual Entry"
            if resume_file:
                r_text = parse_file(resume_file, max_pages=3) # Limit resume to 3 pages
                r_name = resume_file.name
            elif resume_paste.strip():
                r_text = resume_paste
            
            j_text = ""
            j_name = "Manual Entry"
            if jd_file:
                j_text = parse_file(jd_file, max_pages=5) 
                j_name = jd_file.name
            elif jd_paste.strip():
                j_text = jd_paste
           
            elif st.session_state.get("jd_input_content", "").strip():
                j_text = st.session_state["jd_input_content"]
                j_name = f"Auto: {st.session_state.get('jd_role_dropdown', 'Role')}"

            # 3. Clean
            r_text = clean_text(r_text)
            j_text = clean_text(j_text)
            
            # Save
            st.session_state["resume_manual"] = r_text
            st.session_state["jd_manual"] = j_text
            st.session_state["resume_filename"] = r_name
            st.session_state["jd_filename"] = j_name
            
            # Update Session Stats for Sidebar
            st.session_state["last_parse_time"] = datetime.now().strftime("%H:%M:%S")
            st.session_state["parse_count"] = st.session_state.get("parse_count", 0) + 1
            
            # Persist data
            ui_components.save_progress()
            
            # 1. Extract Skills (M2) - Fast
            tech_r, soft_r = extract_skills(r_text)
            tech_j, soft_j = extract_skills(j_text)
            
            r_skills = list(set(tech_r + soft_r))
            j_skills = list(set(tech_j + soft_j))
            
            st.session_state["m2_extracted_skills"] = {
                "resume": r_skills,
                "jd": j_skills,
            }
            
            # 4. Done
            st.session_state["m1_processed"] = True
            update_status(completed=True)

    # -------------------------
    # ADVANCED DASHBOARD (POST-PROCESSING)
    # -------------------------
    if st.session_state.get("m1_processed") and st.session_state["resume_manual"] and st.session_state["jd_manual"]:
        st.markdown("---")
        st.subheader("📊 Document Intelligence Dashboard")
        
        # LINK TO NEW ATS PAGE
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 View Detailed ATS Score & Improvements", type="primary", use_container_width=True):
             st.session_state["nav_page"] = "ATS Report"
             st.rerun()
        
        r_text = st.session_state["resume_manual"]
        j_text = st.session_state["jd_manual"]
        
        # EDITABLE TEXT AREAS (No PII Toggle)
        with st.expander("👁️ View & Edit Extracted Content", expanded=True):
            c_prev1, c_prev2 = st.columns(2)
            with c_prev1:
                new_r = st.text_area("Resume Content (Editable)", r_text, height=300)
                if new_r != st.session_state["resume_manual"]:
                    st.session_state["resume_manual"] = new_r
                    r_text = new_r
                    
                st.download_button(
                    "📥 Download Resume Text",
                    r_text,
                    file_name="resume_extracted.txt",
                )
                
            with c_prev2:
                new_j = st.text_area(
                    "JD Content (Editable)",
                    st.session_state["jd_manual"],
                    height=300,
                )
                if new_j != st.session_state["jd_manual"]:
                    st.session_state["jd_manual"] = new_j
                    j_text = new_j
                st.download_button(
                    "📥 Download JD Text",
                    j_text,
                    file_name="jd_extracted.txt",
                )

        # ANALYTICS GRID
        col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
        
        with col_d1:
            health = analyze_resume_health(r_text)
            score = health["score"]
            gradient_color = "#10B981" if score > 70 else "#F59E0B"
            
            st.markdown(textwrap.dedent(f"""\
                    <div style="background:var(--card-bg); padding:20px; border-radius:16px; border:var(--card-border); text-align:center; height:100%;">
                        <div style="font-weight:700; margin-bottom:15px;">Resume Health</div>
                        <div class="health-score-circle" style="background: conic-gradient({gradient_color} {score}%, var(--muted-color) 0);">
                            <div class="health-score-inner">{score}</div>
                        </div>
                        <div style="text-align:left; font-size:0.85rem; margin-top:15px;">
                            {'<br>'.join(health['checks'])}
                        </div>
                    </div>
                """), unsafe_allow_html=True)
            
        # 2. JD Health
        with col_d2:
            jd_health = analyze_jd_health(j_text)
            jd_score = jd_health["score"]
            jd_gradient = "#3B82F6" if jd_score > 70 else "#F59E0B"
            
            st.markdown(textwrap.dedent(f"""\
                    <div style="background:var(--card-bg); padding:20px; border-radius:16px; border:var(--card-border); text-align:center; height:100%;">
                        <div style="font-weight:700; margin-bottom:15px;">JD Clarity Score</div>
                        <div class="health-score-circle" style="background: conic-gradient({jd_gradient} {jd_score}%, var(--muted-color) 0);">
                            <div class="health-score-inner">{jd_score}</div>
                        </div>
                        <div style="text-align:left; font-size:0.85rem; margin-top:15px;">
                            {'<br>'.join(jd_health['checks'])}
                        </div>
                    </div>
                """), unsafe_allow_html=True)
            
        # 3. Pre-Screen Match
        with col_d3:
            match_score = calculate_pre_match(r_text, j_text)
            match_score = min(100, match_score)  # Cap at 100
            match_gradient = "#8B5CF6" if match_score > 50 else "#EF4444"
            
            st.markdown(textwrap.dedent(f"""\
                    <div style="background:var(--card-bg); padding:20px; border-radius:16px; border:var(--card-border); text-align:center; height:100%;">
                        <div style="font-weight:700; margin-bottom:15px;">Pre-Screen Match</div>
                        <div class="health-score-circle" style="background: conic-gradient({match_gradient} {match_score}%, var(--muted-color) 0);">
                            <div class="health-score-inner">{match_score}%</div>
                        </div>
                        <p style="font-size:0.9rem; margin-top:15px; color:var(--muted-color);">
                            Initial keyword overlap analysis. Proceed to Extraction for deep AI matching.
                        </p>
                    </div>
                """), unsafe_allow_html=True)

        # 4. Key Metrics & Word Cloud
        st.markdown("<br>", unsafe_allow_html=True)
        top_words = get_top_keywords(r_text, 12)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="stat-box"><div class="stat-val">{len(r_text.split())}</div><div class="stat-lbl">Resume Words</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-box"><div class="stat-val">{len(j_text.split())}</div><div class="stat-lbl">JD Words</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            reading_time = calculate_reading_time(r_text)
            st.markdown(
                f'<div class="stat-box"><div class="stat-val">{reading_time}</div><div class="stat-lbl">Read Time</div></div>',
                unsafe_allow_html=True,
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔍 Top Keywords Detected (Quick Glance):**")
        
        # Simple "Tag Cloud" using chips
        tags_html = ""
        for word, count in top_words:
            tags_html += (
                f'<span style="background:rgba(59, 130, 246, 0.1); color:#3B82F6; '
                f'padding:4px 10px; border-radius:12px; margin-right:5px; '
                f'font-size:0.9rem; display:inline-block; margin-bottom:5px;">'
                f'{word} ({count})</span>'
            )
        st.markdown(tags_html, unsafe_allow_html=True)

        # 5. Next Step Call to Action (Green Banner Style)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown(textwrap.dedent("""\
                <div style="background: linear-gradient(90deg, #10B981, #059669); padding: 20px; border-radius: 12px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <div style="font-weight: 700; font-size: 1.2rem;">Ready for Extraction!</div>
                        <div style="font-size: 0.95rem; opacity: 0.9;">Your documents are successfully ingested and analyzed.</div>
                    </div>
                    <div style="font-size: 2rem;">🚀</div>
                </div>
            """), unsafe_allow_html=True)
        
        # Navigation Button Logic (Styled Green via CSS above)
        if st.button("Go to Skill Extraction (Milestone 2) ➡️", type="primary", use_container_width=True):
             st.session_state["nav_page"] = "Milestone 2: Skill Extraction"
             st.query_params["page"] = "m2"
             st.rerun()

    ui_components.render_footer()


if __name__ == "__main__":
    st.set_page_config(page_title="Milestone 1",page_icon="🧭", layout="wide")
    app()
