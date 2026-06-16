# Agentic AI Clinical Decision Support System
### Django · Claude API/GROQ API · SQLite

A multi-agent AI system for clinical decision support built with Django and Anthropic's Claude/GROQ.
Four specialist agents work in sequence — Diagnostic, Risk, Treatment Planning, and Care Pathway — each powered by Claude and coordinated by an Orchestrator.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Python 3.10+ |
| AI agents | Anthropic Claude API (claude-sonnet)/ |  Groq LLaMA 
| Database | SQLite via Django ORM |
| Frontend | Django templates, HTML/CSS, vanilla JS |
| Config | python-dotenv |

---

## Setup instructions

### 1. Clone / download the project
```
cd clinical_ai
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your API key
```bash
cp .env.example .env
```
Open `.env` and add your Anthropic API key or  Groq LLaMA:
```
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY = GSK......
```
Get your key at https://console.anthropic.com/

### 5. Run database migrations
```bash
python manage.py makemigrations patients
python manage.py migrate
```

### 6. Create admin user (optional)
```bash
python manage.py createsuperuser
```

### 7. Seed mock patient data
```bash
python scripts/seed_data.py
```
This creates 20 realistic patients with vitals and lab results (3 critical, 5 high-risk, 12 normal).

### 8. Run the server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

---

## How to use

1. Open the dashboard — you'll see all 20 patients listed with their risk badges
2. Click any patient to open their detail page
3. See their vitals (BP, HR, SpO2, temp, RR, BMI) and full lab panel
4. Click **Run AI analysis** — the 4 agents run in sequence:
   - Diagnostic Agent → differential diagnoses with confidence scores
   - Risk Agent → risk level (low/medium/high/critical) with alert reasons
   - Treatment Agent → medications, interventions, monitoring plan
   - Care Pathway Agent → day-by-day schedule, team tasks, discharge criteria
5. Results appear in 4 tabs. All results are saved to the database automatically.
6. The dashboard shows active risk alerts — click Acknowledge to clear them.

---

## API endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/patients/` | List all patients with latest risk level |
| GET | `/api/patients/<id>/` | Full patient detail + latest AI results |
| POST | `/api/patients/<id>/analyze/` | Run all 4 agents, return full report |
| GET | `/api/alerts/` | All unacknowledged risk alerts (sorted by severity) |
| POST | `/api/alerts/<id>/acknowledge/` | Acknowledge an alert |

---

## Agent architecture

```
Patient data (DB)
      │
      ▼
 Orchestrator
      │
      ├─► DiagnosticAgent  ──► Diagnosis saved to DB
      │         │
      ├─► RiskAgent (uses diagnosis)  ──► RiskAlert saved
      │         │
      ├─► TreatmentAgent (uses diagnosis + risk)  ──► TreatmentPlan saved
      │         │
      └─► CarePathwayAgent (uses all above)  ──► CarePathway saved
```

Each agent:
- Extends `BaseAgent` (handles API client + patient context formatting)
- Has its own `SYSTEM_PROMPT` defining its clinical role
- Returns structured JSON parsed from Claude's response
- Saves its output to the appropriate Django model

---

## Project structure

```
clinical_ai/
├── clinical_ai/         Django project settings & URLs
├── patients/            Patient models, views, API endpoints
├── agents/              All 4 AI agents + orchestrator
├── dashboard/           Frontend views (HTML pages)
├── templates/           Jinja2 HTML templates
├── static/              CSS and JS
├── scripts/             seed_data.py
├── .env.example
├── requirements.txt
└── manage.py
```


- [ ] Alert acknowledgement works
- [ ] Admin panel accessible at /admin/
- [ ] README documents setup and architecture
