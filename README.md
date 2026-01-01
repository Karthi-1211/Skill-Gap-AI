<div align="center">

<img src="banner.png" alt="Skill Gap AI Banner" width="100%">

# 🚀 Skill Gap AI
### *Bridge the Divide Between Potential and Performance*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://skill-gap-ai.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Karthi-1211/Skill-Gap-AI/graphs/commit-activity)

---

**Skill Gap AI** is an all-in-one career development platform designed to empower students and assist HR professionals. Utilizing advanced AI and NLP, the platform provides deep insights into career readiness, automates resume building, and simulates enterprise-level ATS workflows.

[**Explore the App »**](https://skill-gap-ai.streamlit.app/)

</div>

---

## 🌟 Key Features

### 📄 Premium Resume Builder
- **Multi-Step Wizard:** Intelligent questionnaire-based resume generation.
- **16+ Premium Templates:** Choose from Modern, Minimal, Creative, and Executive designs.
- **Live Preview:** Real-time editing with instant visual feedback.
- **High-Fidelity PDF Export:** Professional PDF generation tailored for ATS compatibility.

### 🤖 Smart ATS Score Checker
- **Instant Analysis:** Upload your resume and job description for an instant ATS compatibility score.
- **Detailed Feedback:** Highlights missing keywords, formatting risks, and content gaps.
- **Enterprise Simulation:** Experience how recruiters see your profile with a simulated HR dashboard view.

### 📊 Skill Gap & Milestone Tracking
- **Automated Parsing:** Extracts core skills from resumes and requirements from job descriptions.
- **Gap Analysis:** Visualizes the specific skills you need to acquire for your target role.
- **Progressive Milestones:** 4-stage milestone system (Parsing, Analysis, Personalization, Dashboard) to track career growth.

### 👥 Dual Dashboards
- **Student Dashboard:** Track your applications, view skill gaps, and get personalized recommendations.
- **HR Dashboard:** Manage candidates, review ATS rankings, and streamline the hiring process with AI-driven insights.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | [Streamlit](https://streamlit.io/) (for a seamless, interactive UI) |
| **Language** | [Python](https://www.python.org/) |
| **NLP & AI** | [spaCy](https://spacy.io/), [Transformers](https://huggingface.co/docs/transformers/index), [Sentence-Transformers](https://www.sbert.net/) |
| **Data Processing** | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| **PDF Generation** | [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf), [Jinja2](https://jinja.palletsprojects.com/) |
| **Visualizations** | [Plotly](https://plotly.com/), [Lottie Animations](https://github.com/andymckay/streamlit-lottie) |

---

## 🚀 Getting Started

Follow these steps to set up Skill Gap AI locally:

### 1. Clone the Repository
```bash
git clone https://github.com/Karthi-1211/Skill-Gap-AI.git
cd Skill-Gap-AI
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the Application
```bash
streamlit run main.py
```

---

## 📂 Project Structure

```text
├── .streamlit/          # Streamlit configuration
├── assets/              # Images, Lottie files, and static assets
├── milestone1-4.py      # Core logic for different stages of analysis
├── resume_builder.py    # Multi-step resume generation logic
├── ats_score.py         # ATS evaluation and scoring system
├── pdf_gen.py           # HTML-to-PDF engine with custom templates
├── student_dashboard.py # Personalized student interface
├── hr_dashboard.py      # Recruiter/Management interface
├── home_page.py         # Main landing page entry
└── main.py              # Application entry point
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Made with ❤️ by <b>Karthi</b>
</p>
