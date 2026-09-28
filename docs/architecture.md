# AI Placement Coach — System Architecture

## 1. Overview
**AI Placement Coach** is an autonomous web application designed to prepare collegiate students for competitive campus placements. It models all major rounds of enterprise and product campus recruitment:
1. Cognitive & Technical Aptitude
2. Group Discussion (GD) Preparation & Real-time Simulation
3. AI Mock Interviews (Cloud Engineer, Software Developer, Technical, HR, Managerial)
4. Resume AI Analysis & Resume-Based Questioning
5. Company-Specific Recruitment Syllabus & Patterns
6. Progress Analytics (Radar & Temporal Trends)
7. Full 4-Round Placement Simulation

---

## 2. High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                       Browser Client                        │
│  HTML5 + Vanilla CSS3 + Vanilla JS (Modular ES6 Architecture) │
│  - Web Speech API (Microphone recognition)                 │
│  - SpeechSynthesis API (AI voice output)                    │
│  - Chart.js (Radar, Line, Bar Visualizations)               │
│  - Central API Client (frontend/js/api.js)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Core                     │
│  - JWT Bearer Authentication & Passlib/Bcrypt Hashing       │
│  - CORS Middleware & Static File Mounting                  │
│  - REST API Routers (auth, aptitude, gd, interview, etc.)   │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Database Layer          │ │    Centralized AI Layer    │
│  - SQLAlchemy ORM            │ │  (services/ai_service.py) │
│  - SQLite (Local Dev)        │ │  - Gemini / OpenAI / Groq  │
│  - PostgreSQL Ready          │ │  - Intelligent Fallback    │
│  - Full Relational Models    │ │  - Strict Prompt Isolation │
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 3. Subsystem Breakdown

### 3.1 AI Service & Fallback Architecture
The AI abstraction layer is isolated in `backend/services/ai_service.py`. It guarantees:
- **Zero Prompt Leakage**: Internal system reasoning and hidden prompts are never returned to clients.
- **Provider Agnostic**: Configurable via `AI_PROVIDER`, `AI_API_KEY`, and `AI_MODEL`.
- **Fault-Tolerant Fallback**: When an external API key is absent or network fails, the platform seamlessly switches to curated JSON question banks and rule-based heuristic scoring without crashing.

### 3.2 Aptitude Subsystem
- 50+ collegiate questions across Quantitative, Logical, Verbal, and Data Interpretation.
- Objective backend grading: `score = (correct / total) * 100`.
- Detailed review with step-by-step mathematical explanations and shortcut tricks.

### 3.3 Group Discussion (GD) Multi-Agent Simulator
- Participants: Moderator + Participant 1 (Aarav) + Participant 2 (Priya) + Participant 3 (Rohan) + Candidate.
- Evaluates observable communication metrics: Content, Relevance, Clarity, Structure, Fluency (0-10 scale).

### 3.4 Adaptive Voice Interview Subsystem
- One-question-at-a-time turn loop.
- Dynamic difficulty adjustment: High-scoring answers trigger deeper architectural inquiries; struggling answers receive clarifying foundational questions.
- Browser Web Speech API captures voice directly, converted into text, processed, and responded to via SpeechSynthesis.

### 3.5 Resume Intelligence Subsystem
- Ingests PDF (`pypdf`) and DOCX (`python-docx`).
- Extracts verified candidate skills, featured projects, experience, and education.
- Generates project-specific interview questions without hallucinating unlisted tools.

### 3.6 Flagship Placement Simulation Drive
- Sequential state machine: Aptitude Screening ➔ GD Round ➔ Technical Deep-Dive ➔ HR Behavioral ➔ Comprehensive Preparation Report.
