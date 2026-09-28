# 🚀 AI Placement Coach
> **Prepare Smarter. Practice Harder. Perform Better.**

An autonomous, end-to-end recruitment preparation platform for college students. It simulates the complete campus placement journey—from cognitive aptitude tests and interactive group discussions to adaptive voice mock interviews, resume intelligence, and full 4-round recruitment drives.

---

## 🌟 Key Subsystems & Features

### 1. 🧮 Adaptive Aptitude Engine
- **Categories**: Quantitative Aptitude, Logical Reasoning, Verbal Ability, and Data Interpretation.
- **Exam Environment**: Configurable question count, difficulty levels, interactive timer countdown, question palette navigator, and review flagging.
- **Objective Scoring**: Instant metric grading with accuracy percentage and granular category breakdown.
- **Comprehensive Review**: Step-by-step mathematical derivations and time-saving shortcuts for every single question.

### 2. 👥 Group Discussion (GD) Multi-Agent Simulator
- **Topic Preparation**: 20+ collegiate topics with opening hook statements, structured arguments (for & against), real-world case studies, 30-second elevator speeches, 1-minute persuasive addresses, and pitfalls to avoid.
- **Custom Topic Generator**: Generates complete preparation guides for any topic on-the-fly.
- **Interactive Arena**: Debate in real-time alongside an **AI Moderator** and 3 simulated AI participants (**Aarav**, **Priya**, **Rohan**).
- **Voice & Text Input**: Speak your thoughts via the browser's Web Speech API or type your contributions.
- **5-Dimensional Evaluation**: Evaluates observable communicative performance across Content, Relevance, Clarity, Structure, and Fluency (0-10 scale), with rewritten model answers.

### 3. 🎙️ Adaptive Voice-Driven AI Mock Interviews
- **Specialized Tracks**:
  - **Cloud Engineer**: In-depth AWS architecture (VPC, IAM, EC2, S3, Lambda, Docker, Kubernetes, CloudWatch).
  - **Software Developer**: Algorithms, OOP, Database Indexing, Concurrency, and System Design.
  - **Technical Fundamentals**: Core CS (OS, Networks, DBMS).
  - **HR & Culture Fit**: Behavioral narratives using the STAR method.
  - **Managerial & Leadership**: Strategic trade-offs and team conflict resolution.
  - **Full Mock Interview**: Comprehensive 360° blended evaluation.
- **Turn-by-Turn Dynamic Follow-ups**: Evaluates answers one at a time and adjusts difficulty in real time based on candidate depth.
- **Dual Voice Pipeline**: Microphone voice recognition via Web Speech API + spoken AI questions via SpeechSynthesis.

### 4. 📄 Resume AI Intelligence
- **Universal Ingestion**: Safe parsing of `.pdf` and `.docx` resumes.
- **Structured Extraction**: Extracts candidate skills, featured projects, educational records, and prior internships without hallucination.
- **Resume-Based Mock Interviews**: Generates authentic, project-specific questions based strictly on your uploaded resume.

### 5. 🏢 Company Preparation Tracks
- Detailed hiring syllabus, eligibility cutoffs, and verified question banks for 10 recruiters:
  - **TCS**, **Infosys**, **Wipro**, **Accenture**, **Cognizant**, **Deloitte**, **Capgemini**, **Amazon**, **Microsoft**, **Google**.

### 6. 🚀 Flagship Placement Simulation Drive
- Simulates the entire campus recruitment cycle in one continuous sitting:
  1. **Round 1**: Aptitude & Cognitive Screening
  2. **Round 2**: Group Discussion Round
  3. **Round 3**: Technical Interview Round
  4. **Round 4**: HR & Culture Fit Round
  5. **Final Comprehensive Placement Performance Report**

### 7. 📈 Performance Analytics & Recommendations
- **Interactive Chart.js Visualizations**: Temporal score progression, 5-axis Skill Radar, and weekly practice activity distribution.
- **Calibrated Preparation Readiness**: Weighted calculation across Aptitude (25%), GD (20%), Technical (30%), HR (15%), and Communication (10%).
- **Personalized Recommendations**: Data-backed identification of weakest areas with concrete action items.

### 8. 🛡️ Safe Fallback Mode
- If an AI API key is not configured, the platform automatically switches to offline **Practice Mode** powered by curated JSON banks and heuristic scoring.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js, Web Speech API, SpeechSynthesis API |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2, PyJWT, Bcrypt, python-dotenv |
| **Document Processing** | PyPDF, python-docx |
| **Database** | SQLite (development) / PostgreSQL (production-ready) |
| **AI Abstraction** | Google Gemini / OpenAI / Groq (optional, zero-dependency fallback) |

---

## 📂 Project Directory Structure

```text
AI-Placement-Coach/
├── frontend/
│   ├── index.html                   # Landing Page
│   ├── pages/
│   │   ├── login.html               # Student Login
│   │   ├── register.html            # Profile Registration
│   │   ├── dashboard.html           # Main Hub & Readiness Gauge
│   │   ├── aptitude.html            # Aptitude Test Runner
│   │   ├── aptitude-result.html     # Score Breakdown & Question Review
│   │   ├── gd.html                  # GD Topic Catalog & Guides
│   │   ├── gd-simulator.html        # Multi-Participant GD Arena
│   │   ├── interview.html           # Voice AI Mock Interview Room
│   │   ├── interview-result.html    # Final Interview Evaluation Card
│   │   ├── resume.html              # Resume AI Parser & Questioning
│   │   ├── companies.html           # Top 10 Recruiters Directory
│   │   ├── company-detail.html      # In-depth Company Hiring Track
│   │   ├── progress.html            # Chart.js Analytics & Skill Radar
│   │   ├── simulation.html          # 4-Round Placement Drive
│   │   └── profile.html             # Profile Settings & Target Role
│   ├── css/
│   │   ├── style.css                # Design System & Tokens
│   │   ├── auth.css                 # Login / Register Styles
│   │   ├── dashboard.css            # Widgets & Metrics
│   │   ├── aptitude.css             # Question & Palette Layout
│   │   ├── gd.css                   # Speech Bubbles & Arena
│   │   ├── interview.css            # Voice Waves & Transcript
│   │   ├── resume.css               # Drag & Drop Zone
│   │   ├── companies.css            # Company Grid Cards
│   │   ├── progress.css             # Chart Containers
│   │   ├── simulation.css           # Stepper Wizard & Certificate
│   │   └── responsive.css           # Mobile & Tablet Rules
│   └── js/
│       ├── api.js                   # Central Unified API Client
│       ├── app.js                   # Speech Helpers, Toasts, Auth Check
│       ├── auth.js                  # Login & Signup Handlers
│       ├── dashboard.js             # Dashboard Loader
│       ├── aptitude.js              # Test Engine & Timer
│       ├── aptitude-result.js       # Results Renderer
│       ├── gd.js                    # Topic Search & Modal
│       ├── gd-simulator.js          # Multi-Agent Debate Arena
│       ├── interview.js             # Turn-Based Voice Interviewer
│       ├── interview-result.js      # Interview Report Renderer
│       ├── resume.js                # Document Parser & Action
│       ├── companies.js             # Company Tracks Loader
│       ├── progress.js              # Chart.js Graphs Controller
│       ├── simulation.js            # 4-Stage Drive State Machine
│       └── profile.js               # User Profile Editor
│
├── backend/
│   ├── main.py                      # FastAPI Application Entry
│   ├── config.py                    # Environment Settings
│   ├── dependencies.py              # JWT Auth & Database Session
│   ├── database/
│   │   └── database.py              # SQLAlchemy Connection & Base
│   ├── models/                      # SQLAlchemy Data Models
│   ├── schemas/                     # Pydantic Request & Response Schemas
│   ├── services/                    # Business Logic & AI Abstraction
│   ├── prompts/                     # Isolated AI Prompt Modules
│   └── utils/                       # Security, Hashing, Scoring Helpers
│
├── data/                            # Curated Question & Topic Datasets
│   ├── aptitude_questions.json      # 50+ Collegiate Aptitude Questions
│   ├── gd_topics.json               # 20 Comprehensive GD Guides
│   ├── technical_questions.json     # 30 CS & Cloud Questions
│   ├── hr_questions.json            # 20 Behavioral HR Questions
│   ├── interview_questions.json     # Track-Specific Interview Banks
│   └── companies.json               # 10 Detailed Company Profiles
│
├── docs/
│   ├── architecture.md              # System Architecture
│   ├── api.md                       # REST API Documentation
│   └── setup.md                     # Deployment & Configuration Guide
│
├── uploads/                         # Secure Resume Storage
├── .env.example                     # Environment Configuration Template
├── .gitignore                       # Git Ignore Rules
└── requirements.txt                 # Python Dependencies
```

---

## ⚡ Quick Start Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`. If you wish to enable live generative AI, provide your API key:
```env
AI_PROVIDER=gemini
AI_API_KEY=your_key_here
AI_MODEL=gemini-1.5-flash
```
*If left blank, the platform automatically runs in full offline Practice Mode.*

### 3. Run Application
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Platform
- **Application Web UI**: Open [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger UI)**: Open [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 🧪 Testing

Run automated backend and integration tests:
```bash
pytest
```
Or execute the automated validation suite:
```bash
python -m pytest tests/
```
