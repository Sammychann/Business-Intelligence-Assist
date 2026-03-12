# BI Assist — Transcript & Interview Coach (v3.0)

AI-powered tool for students preparing to **interview professionals** at any company. It provides deep pre-interview intelligence and **real-time live coaching** during the actual interview.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, Vanilla CSS, Vanilla JS (ES6+) |
| **Real-time Comm** | Socket.IO (WebSockets), Web Speech API |
| **Backend** | Python 3.11+, Flask 3.x, Flask-SocketIO |
| **LLM** | Groq Cloud (Llama 3.3 70B & Mixtral) |
| **Search** | DuckDuckGo Search API |
| **Data** | JSON flat-file (business directory, knowledge base, interview history) |

---

## Agentic AI Architecture

BI Assist uses a multi-agent system divided into two phases: **Pre-Interview Prep** and **Live Coaching**.

```text
                        PRE-INTERVIEW                      LIVE INTERVIEW
                ┌────────────────────────────┐    ┌──────────────────────────────┐
                │        Orchestrator        │    │    Live Session Manager      │
                └──────┬──────────────┬──────┘    └──────────────┬───────────────┘
                       │              │                          │
             ┌─────────▼──────┐  ┌────▼───────────┐    ┌─────────▼──────────────┐
             │ CompanyIntel   │  │ Interview      │    │ LiveCoach              │
             │ Agent          │  │ Agent          │    │ Agent                  │
             │                │  │                │    │                        │
             │ ┌────────────┐ │  │ ┌────────────┐ │    │ ┌────────────────────┐ │
             │ │ Bus. Dir + │ │  │ │ Role Search│ │    │ │ Streaming Audio    │ │
             │ │ Web Search │ │  │ │ History KB │ │    │ │ (Web Speech API)   │ │
             │ └────────────┘ │  │ └────────────┘ │    │ └────────────────────┘ │
             │ ┌────────────┐ │  │ ┌────────────┐ │    │ ┌────────────────────┐ │
             │ │ Groq LLM   │ │  │ │ Groq LLM   │ │    │ │ Ultra-Fast LLM     │ │
             │ └────────────┘ │  │ └────────────┘ │    │ └────────────────────┘ │
             └────────────────┘  └────────────────┘    └────────────────────────┘
```

### Agents

| Agent | Phase | Purpose | Knowledge Context |
|-------|-------|---------|-------------------|
| **CompanyIntelAgent** | Pre | Gathers deep, non-obvious company data | Business Directory, Web Search |
| **InterviewAgent** | Pre | Generates smart questions the student should ask | Company Intel output, Role Search, History KB |
| **LiveCoachAgent** | Live | Analyzes real-time transcript chunks to provide talking points | Transcript history, Company Intel output |
| **KnowledgeBaseAgent** | Post | Synthesizes full session transcript into persistent memory | Complete transcript, Company Intel |

---

## Frontend Features & Components

### 1. Pre-Interview Dashboard (`index.html`)
- **Company Insights Tabs**: Snapshot grid, hidden insights, talking points, red flags.
- **Questions to Ask**: Expandable cards with categorization (Strategic, Culture, Role-Specific), predicted answers, and "why ask this" reasoning.
- **Pipeline Trace**: Transparency into agent execution times.

### 2. Live Coaching Overlay (`live.html`)
A standalone, ultra-compact popup window designed to sit side-by-side with Zoom/Teams.
- **At-a-Glance UI**: No scrolling required. Information fits perfectly in a 500x800 window.
- **Live Transcription**: Uses browser Web Speech API to capture conversation.
- **Real-Time Coaching Cards**: 
  - 💡 **Top Insights**: Contextual to what's currently being discussed.
  - 🗣️ **Talking Points**: Suggests specific questions or pivots to make right now.
  - 🔎 **Red Flags & Opportunities**: Actionable alerts based on interviewee statements.
- **Post-Session Knowledge Base**: After ending the session, the full transcript is processed by an agent and saved into the persistent Knowledge Base JSON to inform future interviews.

---

## Functional Requirements

| ID | Requirement | Status |
|----|------------|--------|
| FR-1 | Accept company name + role as input | ✅ |
| FR-2 | Generate deep company intelligence via Web Search + Local DB | ✅ |
| FR-3 | Generate role-specific smart questions and coaching tips | ✅ |
| FR-4 | Open a dedicated "Live Coaching" popup window | ✅ |
| FR-5 | Transcribe interview audio in real-time | ✅ |
| FR-6 | Stream transcript chunks to backend via WebSockets | ✅ |
| FR-7 | Generate real-time coaching cards (insights, talking points, flags) | ✅ |
| FR-8 | Provide an ultra-compact, no-scroll interface for live overlay | ✅ |
| FR-9 | Process completed session transcripts into a persistent Knowledge Base | ✅ |
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

```text
Business-Intelligence-Assist/
├── app.py                          # Flask server + API & Socket.IO routes
├── agents/
│   ├── base_agent.py               # Abstract base with timing/logging
│   ├── orchestrator.py             # Pre-interview pipeline coordinator
│   ├── company_intel_agent.py      # Company analysis agent
│   ├── interview_agent.py          # Question generation agent
│   ├── live_coach_agent.py         # Real-time transcript analyzer
│   ├── knowledge_base_agent.py     # Post-session transcript synthesizer
│   └── knowledge_base.py           # DB Persistence layer
├── services/
│   ├── search.py                   # DuckDuckGo search wrapper
│   └── analyzer.py                 # Groq LLM company analyzer
├── data/
│   ├── business_directory.json     # Curated company directory
│   └── interview_history.json      # Persisted Q&A history + live sessions
├── static/
│   ├── index.html                  # Pre-interview dashboard
│   ├── style.css                   # Main design system
│   ├── script.js                   # Client-side prep logic
│   ├── live.html                   # Live coaching overlay
│   ├── live.css                    # Compact overlay design
│   └── live.js                     # WebSocket + Web Speech API logic
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
# → Dashboard: http://localhost:8000
# → Live Overlay: http://localhost:8000/live?company=X&role=Y
```

---

## Interfacing

### HTTP API

**`POST /api/analyze` (Prep Session)**
Generates pre-interview intelligence.

**`POST /api/process_session` (Post Session)**
Processes a completed live transcript into the Knowledge Base.

**`GET /api/health`**
System health check.

### WebSockets (Live Session)

**`start_session` / `end_session`**
Initialize or terminate real-time coaching state.

**`transcript_chunk`**
Client sends audio transcription text chunks. Backend buffers and triggers `LiveCoachAgent`.

**`coaching_update`**
Backend emits new insights, talking points, and red flags to the client overlay.
