# Business Intelligence Assist — AI Interview Coach & Company Intelligence

An **agentic AI-powered** platform that generates company intelligence dashboards and role-tailored interview coaching. Enter a company name and role — get a summarized intelligence report, tailored interview questions with expected answers, and coaching insights.

---

## Product Overview

**BI Assist** is a Transcript & Interview Coach that uses a multi-agent AI orchestration pipeline to:

1. **Analyze any company** — Financial snapshots, SWOT analysis, risk assessment, competitive positioning, and strategic insights
2. **Generate interview questions** — Role-tailored Q&A categorized as Technical, Company-Specific, and Behavioral
3. **Learn over time** — Persists interview history to avoid repetition and build better questions

### Input
| Field | Description | Example |
|-------|-------------|---------|
| **Company Name** | The company to analyze | Google, Tesla, Stripe |
| **Role** | Role of the person being interviewed | Software Engineer, PM |

### Output
- **Company Intelligence Dashboard** — Super-summarized, insight-focused analysis
- **Interview Coach** — 10-12 tailored questions with expected answers, difficulty ratings, and coaching tips

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT                                  │
│  index.html + style.css + script.js                              │
│  ┌──────────────┐  ┌──────────────────────┐                      │
│  │ Company Input │  │ Role Input           │                      │
│  └──────┬───────┘  └──────────┬───────────┘                      │
│         └─────────┬───────────┘                                  │
│                   ▼                                              │
│         POST /api/analyze { company_name, role }                 │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (app.py)                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                     ORCHESTRATOR                             │  │
│  │                  agents/orchestrator.py                       │  │
│  │                                                              │  │
│  │  1. Dispatch ───► CompanyIntelAgent                          │  │
│  │  2. Pass data ──► InterviewAgent                             │  │
│  │  3. Merge results                                            │  │
│  └──────┬──────────────────────────┬────────────────────────────┘  │
│         │                          │                               │
│         ▼                          ▼                               │
│  ┌──────────────────┐   ┌──────────────────────┐                  │
│  │ CompanyIntelAgent │   │ InterviewAgent        │                 │
│  │                   │   │                       │                 │
│  │ ► search_company()│   │ ► search_role_context()│                │
│  │ ► analyze_company │   │ ► KnowledgeBase.get() │                 │
│  │   (Groq LLM)     │   │ ► generate_questions  │                 │
│  │                   │   │   (Groq LLM)          │                 │
│  │ Returns:          │   │ ► KnowledgeBase.save()│                 │
│  │  Dashboard data   │   │                       │                 │
│  └──────┬────────────┘   │ Returns:              │                 │
│         │                │  Interview Q&A        │                 │
│         │                └───────────┬───────────┘                 │
│         └────────────────────────────┘                             │
└───────────────────────────────────────────────────────────────────┘
```

### Agent Communication Flow

```
┌──────────────┐     context      ┌──────────────────┐
│              │ ──────────────►  │                    │
│ Orchestrator │                  │ CompanyIntelAgent  │
│              │ ◄──────────────  │                    │
└──────┬───────┘  company_report  └──────────────────  │
       │                         ────────────────────┘
       │  context + company_report
       │
       ▼
┌──────────────────┐
│                   │    ┌─────────────────┐
│  InterviewAgent   │───►│  KnowledgeBase  │
│                   │◄───│  (JSON store)   │
└──────────────────┘    └─────────────────┘
       │
       │  interview_questions + coaching_tips
       ▼
┌──────────────┐
│ Orchestrator │ ──► Merged Response ──► Client
└──────────────┘
```

### Knowledge Bases

| # | Knowledge Base | Source | Used By |
|---|----------------|--------|---------|
| 1 | **Company Directory** | DuckDuckGo web search (overview, financials, news, competitors) | CompanyIntelAgent |
| 2 | **Search Service** | Real-time web search for role-specific context | InterviewAgent |
| 3 | **Previous Interview Questions** | Local JSON store (`data/interview_history.json`) | InterviewAgent |

---

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python | 3.10+ |
| Web Framework | Flask | 3.1.0 |
| CORS | Flask-CORS | 5.0.1 |
| LLM Provider | Groq API (llama-3.3-70b) | 0.25.0 |
| Web Search | duckduckgo-search | 7.5.3 |
| Env Management | python-dotenv | 1.1.0 |
| Frontend | HTML5 / CSS3 / JavaScript | — |
| Font | Inter (Google Fonts) | — |
| Color Theme | White / Black / Orange | — |

---

## Project Structure

```
Business-Intelligence-Assist/
├── app.py                          # Flask server + API endpoint
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API keys)
├── .gitignore                      # Git ignore rules
├── README.md                       # This documentation
│
├── agents/                         # Agentic AI orchestration layer
│   ├── __init__.py                 # Package init (exports Orchestrator)
│   ├── base_agent.py               # Abstract base agent (logging, timing)
│   ├── orchestrator.py             # Central pipeline coordinator
│   ├── company_intel_agent.py      # Company intelligence gathering
│   ├── interview_agent.py          # Interview Q&A generation
│   └── knowledge_base.py           # Persistent Q&A knowledge base
│
├── services/                       # External service integrations
│   ├── __init__.py                 # Package init
│   ├── search.py                   # DuckDuckGo search + role context
│   └── analyzer.py                 # Groq LLM analysis
│
├── data/                           # Persistent data storage
│   └── interview_history.json      # Q&A history (auto-populated)
│
└── static/                         # Frontend (single-page app)
    ├── index.html                  # Page structure (two inputs, tabbed dashboard)
    ├── style.css                   # White/black/orange design system
    └── script.js                   # Client logic (tabs, Q&A cards, pipeline trace)
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- A Groq API key ([console.groq.com](https://console.groq.com))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Business-Intelligence-Assist.git
cd Business-Intelligence-Assist

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
# Edit .env and set GROQ_API_KEY=your_key_here
```

---

## Running the Application

```bash
python app.py
```

The server starts at `http://localhost:8000` with debug mode enabled.

### Production

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:8000 --workers 4
```

---

## API Reference

### `POST /api/analyze`

Analyze a company and generate interview coaching.

**Request:**
```json
{
  "company_name": "Google",
  "role": "Software Engineer"
}
```

**Response (200):**
```json
{
  "company_name": "Google",
  "role_analyzed": "Software Engineer",
  "executive_summary": "...",
  "financial_snapshot": { ... },
  "business_model_analysis": "...",
  "competitive_positioning": { ... },
  "swot_analysis": { ... },
  "market_growth_outlook": { ... },
  "risk_assessment": { ... },
  "ai_opportunities": ["..."],
  "key_insights": ["..."],
  "analysis_confidence": "High",
  "interview_questions": [
    {
      "question": "...",
      "expected_answer": "...",
      "category": "technical",
      "difficulty": "medium",
      "reasoning": "..."
    }
  ],
  "coaching_tips": ["..."],
  "_pipeline": {
    "total_elapsed_seconds": 25.4,
    "agent_trace": [
      { "agent": "CompanyIntelAgent", "status": "success", "elapsed_seconds": 15.2 },
      { "agent": "InterviewAgent", "status": "success", "elapsed_seconds": 10.1 }
    ]
  }
}
```

### `GET /api/health`

```json
{
  "status": "ok",
  "service": "Business Intelligence Assist",
  "version": "2.0.0",
  "agents": ["CompanyIntelAgent", "InterviewAgent"]
}
```

---

## Agents

### 1. CompanyIntelAgent

**Purpose:** Gathers company data and produces the summarized intelligence dashboard.

**Knowledge Bases Used:**
- Company Directory (DuckDuckGo search)
- Search Service (financial, news, competitor queries)

**Output:** Executive summary, financial snapshot, SWOT, risk assessment, competitive positioning, market outlook, AI opportunities, key insights.

### 2. InterviewAgent

**Purpose:** Generates role-tailored interview questions with expected answers.

**Knowledge Bases Used:**
- Company intelligence (from CompanyIntelAgent)
- Search Service (role-specific web search)
- Previous Interview Questions (local JSON store)

**Output:** 10-12 categorized questions (Technical / Company-Specific / Behavioral) with expected answers, difficulty ratings, reasoning, and coaching tips.

### 3. Orchestrator

**Purpose:** Coordinates the agent pipeline sequentially.

**Flow:** Input → CompanyIntelAgent → InterviewAgent → Merged Response

---

## Non-Functional Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Performance** | Agent pipeline completes in 20-40s. LLM model fallback chain prevents total failure. |
| **Reliability** | Three-model fallback chain (llama-3.3-70b → llama3-70b → mixtral-8x7b). Graceful search failure handling. |
| **Scalability** | Stateless Flask server supports horizontal scaling via Gunicorn workers. |
| **Security** | API key stored in `.env`, not in source code. Input validation on all endpoints. CORS enabled. |
| **Maintainability** | Clean separation: agents → services → app. Each agent is independently testable. |
| **Data Persistence** | Interview history persisted in `data/interview_history.json` with deduplication. |
| **Observability** | Structured logging with agent names. Pipeline trace with per-agent timing returned to client. |
| **Extensibility** | New agents can be added by extending `BaseAgent` and registering in the Orchestrator. |

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Empty company name | 400: "Company name is required" |
| Empty role | 400: "Role is required" |
| Company name > 200 chars | 400: "Company name too long" |
| Role > 100 chars | 400: "Role description too long" |
| Missing GROQ_API_KEY | 400: "GROQ_API_KEY not set" |
| All LLM models fail | 502: "Analysis failed" |
| DuckDuckGo fails | Graceful fallback with limited data |
| Invalid LLM JSON | Regex extraction fallback, then next model |

---

## License

This project is open source. See the repository for license details.
