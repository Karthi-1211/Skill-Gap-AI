import streamlit as st
import time
try:
    import streamlit_analytics2 as streamlit_analytics
except ImportError:
    # Fallback if not installed yet
    class streamlit_analytics:
        @staticmethod
        def track():
            from contextlib import contextmanager
            @contextmanager
            def internal_track():
                yield
            return internal_track()

# Page config
st.set_page_config(
    page_title="AI Skill Gap Analyzer",
    page_icon="🚀",
    layout="wide" 
)

# Start Tracking
with streamlit_analytics.track(unsafe_password="admin123"):
    # -------------------------
    # UTILITIES & SETUP
    # ------------------------
    from components import navigate_to, PAGE_MAP
    import components

    # Pre-load heavy modules to prevent navigation lag
    import milestone3 
    import milestone2
    import milestone1

    # Load persisted session data to handle reloads/navigation
    components.load_progress()

    # Handle Query Parameters for Navigation
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Home"

    # Initialize Mock Database (Jobs & Applications)
    if "jobs" not in st.session_state:
        st.session_state["jobs"] = [
            {"id": "JOB-101", "role": "Associate Data Scientist", "company": "TechCorp AI", "location": "Remote", "min_score": 85},
            {"id": "JOB-102", "role": "Frontend Developer (React)", "company": "StartupX", "location": "New York", "min_score": 80},
            {"id": "JOB-103", "role": "DevOps Engineer", "company": "CloudSystems", "location": "San Francisco", "min_score": 75},
            {"id": "JOB-104", "role": "Product Manager", "company": "Innovate Ltd", "location": "London", "min_score": 90}
        ]

    if "applications" not in st.session_state:
        st.session_state["applications"] = [
            {"job_id": "JOB-102", "applicant": "Alamanda Balu Karthik", "job_role": "Frontend Developer (React)", "score": 63, "status": "Screening", "applied_at": "2 days ago", "resume_version": "v1.0", "company": "StartupX"},
            {"job_id": "JOB-101", "applicant": "Alice Chen", "job_role": "Associate Data Scientist", "score": 88, "status": "Interview", "applied_at": "1 day ago", "resume_version": "v1.0", "company": "TechCorp AI"},
            {"job_id": "JOB-103", "applicant": "Marcus Johnson", "job_role": "DevOps Engineer", "score": 72, "status": "Pending", "applied_at": "3 hours ago", "resume_version": "v1.2", "company": "CloudSystems"},
            {"job_id": "JOB-104", "applicant": "Sarah Williams", "job_role": "Product Manager", "score": 91, "status": "Accepted", "applied_at": "1 week ago", "resume_version": "v2.0", "company": "Innovate Ltd"},
            {"job_id": "JOB-102", "applicant": "David Kim", "job_role": "Frontend Developer (React)", "score": 55, "status": "Rejected", "applied_at": "2 weeks ago", "resume_version": "v1.0", "company": "StartupX"},
            {"job_id": "JOB-101", "applicant": "Priya Patel", "job_role": "Associate Data Scientist", "score": 79, "status": "Screening", "applied_at": "3 days ago", "resume_version": "v1.1", "company": "TechCorp AI"}
        ]

    if "applications" in st.session_state:
        for app in st.session_state["applications"]:
            if app.get("applicant") in ["Current User", "Alexander Smith"]:
                app["applicant"] = "Alamanda Balu Karthik"

    query_params = st.query_params
    if "page" in query_params:
        qp = query_params["page"]
        if isinstance(qp, list):
            qp = qp[0]
        
        # Reverse lookup for case-insensitive matching
        qp_lower = qp.lower()
        if qp_lower in PAGE_MAP:
            st.session_state["nav_page"] = PAGE_MAP[qp_lower]

    if "redirect_to" in st.session_state:
        st.session_state["nav_page"] = st.session_state["redirect_to"]
        # Update URL query param to reflect redirect
        reverse_page_map = {v: k for k, v in PAGE_MAP.items()}
        if st.session_state["nav_page"] in reverse_page_map:
            st.query_params["page"] = reverse_page_map[st.session_state["nav_page"]]
        del st.session_state["redirect_to"]

    current_page = st.session_state["nav_page"]

    # -------------------------
    # PAGE SCROLL HANDLING
    # -------------------------
    if "previous_page" not in st.session_state:
        st.session_state["previous_page"] = current_page

    if st.session_state["previous_page"] != current_page:
        st.session_state["previous_page"] = current_page
        components.scroll_to_top(smooth=False)

    # -------------------------
    # ROUTING
    # -------------------------

    with st.spinner("Loading Space..."):
        if current_page == "Home":
            import home_page
            home_page.app()

        elif current_page == "Milestone 1: Data Ingestion":
            import milestone1
            milestone1.app()

        elif current_page == "Milestone 2: Skill Extraction":
            import milestone2
            milestone2.app()

        elif current_page == "Milestone 3: Gap Analysis":
            milestone3.app()

        elif current_page == "Milestone 4: Dashboard & Report":
            import milestone4
            milestone4.app()


        elif current_page == "ATS Report":
            import ats_score
            ats_score.app()



        elif current_page == "Feedback":
            import feedback
            feedback.app()

        elif current_page == "Contact Us":
            import contact
            contact.app()

        elif current_page == "HR Dashboard":
            import hr_dashboard
            hr_dashboard.app()

        elif current_page == "Student Dashboard":
            import student_dashboard
            student_dashboard.app()

        elif current_page == "Resume Builder":
            import resume_builder
            resume_builder.app()
