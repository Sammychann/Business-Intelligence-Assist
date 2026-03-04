# BI Assist — Transcript & Interview Coach

AI-powered tool for students preparing to **interview professionals** at any company. Enter a company + role → get deep insights, smart questions to ask, and coaching tips.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, Vanilla CSS, Vanilla JS (ES6+) |
| **Backend** | Python 3.11+, Flask 3.x |
| **LLM** | Groq Cloud (Llama 3.3 70B) |
| **Search** | DuckDuckGo Search API |
| **Fonts** | Google Fonts (Inter) |
| **Data** | JSON flat-file (business directory, interview history) |

---

## Agentic AI Architecture

```
                          ┌──────────────┐
                          │   Frontend   │
                          │  HTML/CSS/JS │
                          └──────┬───────┘
                                 │ POST /api/analyze
                                 ▼
                          ┌──────────────┐
                          │  Flask API   │
                          │   app.py     │
                          └──────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     ORCHESTRATOR       │
                    │  orchestrator.py       │
                    │                        │
                    │  Sequential Pipeline:  │
                    │  Agent 1 → Agent 2     │
                    └───┬──────────────┬─────┘
                        │              │
              ┌─────────▼──────┐  ┌────▼───────────┐
              │ CompanyIntel   │  │ Interview      │
              │ Agent          │  │ Agent          │
              │                │  │                │
              │ ┌────────────┐ │  │ ┌────────────┐ │
              │ │ Business   │ │  │ │ Role       │ │
              │ │ Directory  │ │  │ │ Search     │ │
              │ │ (25 co.)   │ │  │ │ (DDG)     │ │
              │ ├────────────┤ │  │ ├────────────┤ │
              │ │ Web Search │ │  │ │ Interview  │ │
              │ │ (DDG)      │ │  │ │ History KB │ │
              │ ├────────────┤ │  │ ├────────────┤ │
              │ │ Groq LLM   │ │  │ │ Groq LLM   │ │
              │ │ (Analyze)  │ │  │ │ (Generate) │ │
              │ └────────────┘ │  │ └────────────┘ │
              └────────────────┘  └────────────────┘
```

### Agents

| Agent | Purpose | Knowledge Bases |
|-------|---------|----------------|
| **CompanyIntelAgent** | Gathers company data, generates insight-focused analysis | Business Directory (local JSON), Web Search (DuckDuckGo), Groq LLM |
| **InterviewAgent** | Generates smart questions the student should ASK | Company Report (from Agent 1), Role-specific Search, Interview History (local JSON), Groq LLM |
| **Orchestrator** | Sequential pipeline coordinator | Dispatches agents, merges outputs, tracks timing |
| **BaseAgent** | Abstract base class | Provides timing, logging, error handling |
| **KnowledgeBase** | Persistence layer | Reads/writes interview history to avoid question repetition |

### Data Flow

```
Input (company, role)
  → Orchestrator
    → CompanyIntelAgent
      → Lookup business_directory.json (fuzzy match)
      → DuckDuckGo search (company news)
      → Groq LLM → { snapshot, hidden_insights, talking_points, red_flags }
    → InterviewAgent
      → Receives company report from Agent 1
      → DuckDuckGo search (role-specific context)
      → Loads interview_history.json (avoid repeats)
      → Groq LLM → { questions[], coaching_tips[] }
  → Merged JSON response → Frontend renders dashboard
```

---

## Frontend Features & Components

### Pages & Sections

| Component | Description |
|-----------|-------------|
| **Hero Section** | Headline, subtitle, company + role input form, CTA button |
| **Loading Overlay** | Animated orb + step-by-step agent progress messages |
| **Tab Bar** | Two tabs: "Company Insights" and "Questions to Ask" |
| **Company Insights Tab** | Snapshot grid, hidden insights, talking points, red flags/opportunities |
| **Questions to Ask Tab** | Expandable question cards with category filters and coaching tips |
| **Pipeline Trace** | Agent timing breakdown (name, status, elapsed seconds) |

### Company Insights Components

| Component | What It Shows |
|-----------|--------------|
| **Company at a Glance** | 5-field grid: What They Do, Industry, Size, Founded, HQ |
| **Hidden Insights** | 5-7 numbered AI-synthesized insights with significance explanations |
| **Talking Points** | 4-6 bullet points to sound impressively prepared |
| **Red Flags & Opportunities** | Color-coded cards (rose/green) with probe questions to ask |

### Questions to Ask Components

| Component | What It Shows |
|-----------|--------------|
| **Category Filters** | Pill buttons: All, Role-Specific, Strategic, Culture & Team |
| **Question Cards** | Expandable cards with number, text, category badge, difficulty badge |
| **Expected Answer** | "What They'll Likely Say" — predicted interviewee response |
| **Why Ask This** | Strategic reasoning — what intel the student gains |
| **Coaching Tips** | 5-7 tips on conducting the interview (active listening, follow-ups) |

### Interactivity

- **Expand/collapse** — Click any question card header to reveal answer + reasoning
- **Category filtering** — Filter questions by Role-Specific / Strategic / Culture & Team
- **Tab switching** — Toggle between Company Insights and Questions to Ask
- **Error handling** — Inline error banner with retry guidance
- **Loading states** — Button spinner + overlay with animated pipeline steps

---

## Functional Requirements

| ID | Requirement | Status |
|----|------------|--------|
| FR-1 | Accept company name + role as input | ✅ |
| FR-2 | Lookup company in local business directory (25 companies) | ✅ |
| FR-3 | Supplement with real-time web search via DuckDuckGo | ✅ |
| FR-4 | Generate insight-focused company intelligence (not generic public info) | ✅ |
| FR-5 | Generate 10-12 smart questions the student should ASK | ✅ |
| FR-6 | Categorize questions as role_specific / strategic / culture_insight | ✅ |
| FR-7 | Include expected answers and "why ask this" reasoning | ✅ |
| FR-8 | Persist interview history to avoid question repetition | ✅ |
| FR-9 | Provide coaching tips for conducting the interview | ✅ |
| FR-10 | Display pipeline trace with agent timing | ✅ |

---

## Non-Functional Requirements

| ID | Requirement | Implementation |
|----|------------|---------------|
| NFR-1 | **Response Time** < 45s end-to-end | Groq inference (~10s/agent), parallel-ready architecture |
| NFR-2 | **Error Resilience** | 3-model fallback chain (Llama 3.3 70B → Llama3 70B → Mixtral 8x7B) |
| NFR-3 | **Graceful Degradation** | Works without business directory (web-search-only fallback) |
| NFR-4 | **Input Validation** | Company name ≤200 chars, role ≤100 chars, required field checks |
| NFR-5 | **XSS Prevention** | All user input HTML-escaped before DOM insertion |
| NFR-6 | **Responsive Design** | Mobile-first CSS with breakpoints at 768px |
| NFR-7 | **Accessibility** | Semantic HTML, ARIA labels, keyboard-navigable tabs |
| NFR-8 | **Logging** | Structured logging with timestamps and agent names |
| NFR-9 | **Maintainability** | Modular agent architecture, single-responsibility classes |
| NFR-10 | **Extensibility** | New agents added by extending BaseAgent + registering in Orchestrator |

---

## Project Structure

```
Business-Intelligence-Assist/
├── app.py                          # Flask server + API routes
├── agents/
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base with timing/logging
│   ├── orchestrator.py             # Sequential pipeline coordinator
│   ├── company_intel_agent.py      # Company analysis agent
│   ├── interview_agent.py          # Question generation agent
│   └── knowledge_base.py           # Interview history persistence
├── services/
│   ├── search.py                   # DuckDuckGo search wrapper
│   └── analyzer.py                 # Groq LLM company analyzer
├── data/
│   ├── business_directory.json     # 25-company curated directory
│   └── interview_history.json      # Persisted Q&A history
├── static/
│   ├── index.html                  # Single-page frontend
│   ├── style.css                   # White/black/orange design system
│   └── script.js                   # Client-side rendering + interactivity
├── requirements.txt
├── .env                            # GROQ_API_KEY
└── README.md
```

---

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
echo GROQ_API_KEY=your_key_here > .env

# Run
python app.py
# → http://localhost:8000
```

---

## API

### `POST /api/analyze`

```json
// Request
{ "company_name": "Google", "role": "Product Manager" }

// Response
{
  "company_name": "Google",
  "company_snapshot": { "what_they_do": "...", "industry": "...", "size": "...", "founded": "...", "headquarters": "..." },
  "hidden_insights": [{ "insight": "...", "significance": "..." }],
  "talking_points": ["..."],
  "red_flags_opportunities": [{ "item": "...", "type": "red_flag|opportunity", "probe_question": "..." }],
  "interview_questions": [{ "question": "...", "expected_answer": "...", "category": "...", "difficulty": "...", "why_ask_this": "..." }],
  "coaching_tips": ["..."],
  "role_analyzed": "Product Manager",
  "analysis_confidence": "High",
  "_pipeline": { "total_elapsed_seconds": 27.65, "agent_trace": [...] }
}
```

### `GET /api/health`

```json
{ "status": "ok", "service": "Business Intelligence Assist", "version": "2.0.0" }
```
