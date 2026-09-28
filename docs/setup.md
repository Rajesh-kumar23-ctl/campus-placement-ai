# AI Placement Coach — Setup & Deployment Guide

## 1. Prerequisites
- Python 3.11+
- Git
- Web browser (Chrome, Edge, Brave, or Safari with Web Speech support)

---

## 2. Installation & Local Development

### Step 1: Clone Repository
```bash
git clone <repository_url>
cd intweb
```

### Step 2: Set Up Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configurations are pre-tuned for local development.

If you have an AI API key (Google Gemini, OpenAI, or Groq), configure:
```env
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
```
*Note: If `AI_PROVIDER` and `AI_API_KEY` are left blank, the platform automatically runs in Practice Mode with full offline question banks and heuristic evaluation.*

---

## 3. Running the Application

### Option A: Unified FastAPI Server (Serves Backend API + Frontend on port 8000)
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
```text
http://localhost:8000
```
Interactive Swagger API documentation is available at:
```text
http://localhost:8000/api/docs
```

### Option B: Separate Frontend Dev Server
If serving the frontend via Live Server (port 5500) or static HTTP:
- Run backend: `uvicorn backend.main:app --port 8000 --reload`
- Serve frontend from `frontend/` on port 5500. `frontend/js/api.js` automatically routes calls to `http://localhost:8000`.

---

## 4. Production Deployment

### Backend (Render / Railway / AWS EC2)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- For production database, change `DATABASE_URL` to a PostgreSQL connection string:
  ```env
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  ```

### Frontend (Static Deployments like Vercel / Netlify)
- Set Publish Directory to: `frontend/`
- Set `API_BASE_URL` in `frontend/js/api.js` to your deployed backend URL.
