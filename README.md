# Business Intelligence Assist — Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [API Reference](#api-reference)
9. [How It Works](#how-it-works)
10. [Report Schema](#report-schema)
11. [LLM Prompt Engineering](#llm-prompt-engineering)
12. [Error Handling](#error-handling)
13. [Customization Guide](#customization-guide)
14. [Deployment](#deployment)
15. [Troubleshooting](#troubleshooting)
16. [License](#license)

---

## Overview

**Business Intelligence Assist** is an AI-powered web application that generates comprehensive company intelligence reports. Enter any company name and get a structured report covering:

- Executive Summary
- Financial Snapshot
- Business Model Analysis
- Competitive Positioning
- SWOT Analysis
- Market & Growth Outlook
- Risk Assessment
- AI / Technology Opportunities
- Key Strategic Insights
- Confidence Score

Reports are generated using a combination of real-time web search (DuckDuckGo) and large language model analysis (Groq API).

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│    index.html  +  style.css  +  script.js               │
│    (Form submission → fetch('/api/analyze') → render)   │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP POST (JSON)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    FLASK SERVER                          │
│                      app.py                             │
│                                                         │
│  POST /api/analyze                                      │
│    1. Validate input                                    │
│    2. Call search_company() → DuckDuckGo                │
│    3. Call analyze_company() → Groq LLM                 │
│    4. Return JSON report                                │
└─────────┬────────────────────────┬──────────────────────┘
          │                        │
          ▼                        ▼
┌──────────────────┐   ┌───────────────────────┐
│  services/       │   │  services/            │
│  search.py       │   │  analyzer.py          │
│                  │   │                       │
│  DuckDuckGo      │   │  Groq API             │
│  Text Search     │   │  llama-3.3-70b        │
│  News Search     │   │  System Prompt        │
│  Data Extraction │   │  JSON Parsing         │
└──────────────────┘   └───────────────────────┘
```

---

## Tech Stack

| Component        | Technology                | Version   |
|-----------------|---------------------------|-----------|
| Backend         | Python                    | 3.10+     |
| Web Framework   | Flask                     | 3.1.0     |
| CORS            | Flask-CORS                | 5.0.1     |
| LLM Provider    | Groq API                  | 0.25.0    |
| Web Search      | duckduckgo-search         | 7.5.3     |
| Env Management  | python-dotenv             | 1.1.0     |
| HTTP Client     | requests                  | 2.32.3    |
| Frontend        | HTML5 / CSS3 / JavaScript | —         |
| Font            | Inter (Google Fonts)      | —         |

---

## Project Structure

```
Business-Intelligence-Assist/
├── app.py                  # Flask application (main entry point)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── .gitignore              # Git ignore rules
├── README.md               # Project readme
├── DOCUMENTATION.md        # This file
├── services/
│   ├── __init__.py         # Package init
│   ├── search.py           # DuckDuckGo search service
│   └── analyzer.py         # Groq LLM analysis service
└── static/
    ├── index.html           # Single-page frontend
    ├── style.css            # Stylesheet (light theme)
    └── script.js            # Client-side application logic
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- A Groq API key (get one at https://console.groq.com)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Business-Intelligence-Assist.git
cd Business-Intelligence-Assist

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
#    Edit .env and set your GROQ_API_KEY
```

---

## Configuration

All configuration is managed through the `.env` file:

| Variable       | Required | Description                              | Example                                    |
|---------------|----------|------------------------------------------|--------------------------------------------|
| `GROQ_API_KEY` | Yes      | Your Groq API key for LLM access        | `gsk_abc123...`                            |
| `PORT`         | No       | Server port (default: 8000)             | `8000`                                     |

### Getting a Groq API Key

1. Visit https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it into your `.env` file

---

## Running the Application

### Development Mode

```bash
python app.py
```

The server starts at `http://localhost:8000` with auto-reload enabled.

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:8000 --workers 4
```

---

## API Reference

### `GET /`

Serves the frontend single-page application.

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "Business Intelligence Assist"
}
```

### `POST /api/analyze`

Analyze a company and return a structured intelligence report.

**Request:**
```json
{
  "company_name": "Tesla"
}
```

**Headers:** `Content-Type: application/json`

**Response (200):**
```json
{
  "company_name": "Tesla",
  "executive_summary": "...",
  "financial_snapshot": {
    "revenue": "$97.7B",
    "revenue_trend": "Growing",
    "employees": "125,665",
    "funding_status": "$20.2B",
    "profitability_status": "Not Public"
  },
  "business_model_analysis": "...",
  "competitive_positioning": {
    "market_category": "Electric Vehicle and Clean Energy",
    "differentiation": "...",
    "market_maturity": "Established"
  },
  "swot_analysis": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."]
  },
  "market_growth_outlook": {
    "industry_trend": "...",
    "growth_potential": "High",
    "expansion_opportunities": "..."
  },
  "risk_assessment": {
    "regulatory_risk": "Medium",
    "competitive_risk": "High",
    "market_risk": "Medium",
    "operational_risk": "Medium",
    "financial_risk": "Low",
    "overall_risk_score": 6
  },
  "ai_opportunities": ["..."],
  "key_insights": ["..."],
  "analysis_confidence": "High",
  "_model_used": "llama-3.3-70b-versatile"
}
```

**Error Response (400):**
```json
{
  "error": "Company name is required"
}
```

**Error Response (502):**
```json
{
  "error": "Analysis failed: All models failed."
}
```

---

## How It Works

### Step 1: Web Search Enrichment (`services/search.py`)

When a company name is submitted, the search service:

1. **General search** — Queries DuckDuckGo for "{company_name} company overview" (8 results)
2. **Financial search** — Queries for "{company_name} revenue employees funding" (5 results)
3. **News search** — Fetches recent news headlines about the company (5 results)
4. **Competitor search** — Queries for "{company_name} competitors alternatives" (3 results)
5. **Field extraction** — Uses regex patterns to extract structured fields (industry, headquarters, founded year, CEO, revenue, employee count) from the aggregated snippets

The output is a combined payload of structured data + raw snippets, sent to the LLM.

### Step 2: LLM Analysis (`services/analyzer.py`)

The analyzer:

1. Constructs a system prompt containing the full analysis specification (10 sections, format rules, confidence scoring)
2. Sends the search payload as the user message
3. Calls Groq API with `response_format: json_object` for strict JSON output
4. Uses `temperature: 0.2` and `top_p: 0.9` for analytical stability
5. Validates required keys exist in the response
6. Falls back through models if the primary model fails:
   - Primary: `llama-3.3-70b-versatile`
   - Fallback 1: `llama3-70b-8192`
   - Fallback 2: `mixtral-8x7b-32768`

### Step 3: Frontend Rendering (`static/script.js`)

The JavaScript client:

1. Submits the company name via `fetch('/api/analyze')`
2. Shows animated loading steps during the ~30-40s analysis
3. Parses the JSON response and renders 10 dashboard sections:
   - Executive Summary card
   - Financial Snapshot grid (revenue, trend, employees, funding, profitability)
   - Competitive Positioning grid (market, differentiation, maturity)
   - Business Model Analysis paragraph
   - SWOT 2×2 grid with color-coded quadrants
   - Market Outlook grid with growth badge
   - Risk Assessment with animated bar meters and overall score
   - AI Opportunities list
   - Key Insights numbered list

---

## Report Schema

The full JSON schema returned by the `/api/analyze` endpoint:

| Field                              | Type     | Description                                             |
|------------------------------------|----------|---------------------------------------------------------|
| `company_name`                     | string   | Analyzed company name                                   |
| `executive_summary`                | string   | 120-150 word overview                                   |
| `financial_snapshot.revenue`       | string   | Latest known revenue                                    |
| `financial_snapshot.revenue_trend` | string   | Revenue direction (Growing/Declining/Stable)            |
| `financial_snapshot.employees`     | string   | Employee count                                          |
| `financial_snapshot.funding_status`| string   | Funding raised or "Not Public"                          |
| `financial_snapshot.profitability_status` | string | Profitable/Unprofitable/Not Public               |
| `business_model_analysis`          | string   | Revenue streams, customers, pricing, channels           |
| `competitive_positioning.market_category` | string | Industry/market category                         |
| `competitive_positioning.differentiation` | string | Key competitive advantages                       |
| `competitive_positioning.market_maturity` | string | Emerging/Growth/Established/Saturated            |
| `swot_analysis.strengths`          | string[] | 3-5 strength bullet points                              |
| `swot_analysis.weaknesses`         | string[] | 3-5 weakness bullet points                              |
| `swot_analysis.opportunities`      | string[] | 3-5 opportunity bullet points                           |
| `swot_analysis.threats`            | string[] | 3-5 threat bullet points                                |
| `market_growth_outlook.industry_trend` | string | Industry growth direction                            |
| `market_growth_outlook.growth_potential` | string | Low/Moderate/High/Aggressive                       |
| `market_growth_outlook.expansion_opportunities` | string | Geographic/product expansion notes            |
| `risk_assessment.regulatory_risk`  | string   | Low/Medium/High                                         |
| `risk_assessment.competitive_risk` | string   | Low/Medium/High                                         |
| `risk_assessment.market_risk`      | string   | Low/Medium/High                                         |
| `risk_assessment.operational_risk` | string   | Low/Medium/High                                         |
| `risk_assessment.financial_risk`   | string   | Low/Medium/High                                         |
| `risk_assessment.overall_risk_score` | number | 1-10 (1=Very Stable, 10=Extremely Risky)               |
| `ai_opportunities`                 | string[] | AI/automation improvement areas                         |
| `key_insights`                     | string[] | 5 strategic insight bullets                             |
| `analysis_confidence`              | string   | Low/Medium/High                                         |
| `_model_used`                      | string   | Which LLM model was used for analysis                   |

---

## LLM Prompt Engineering

The system prompt in `services/analyzer.py` is designed for:

- **Strict JSON output** — The LLM is instructed to return ONLY valid JSON, no markdown or commentary
- **Data grounding** — The prompt requires the LLM to use only provided data + widely known public facts
- **Uncertainty marking** — Missing data must be marked as "Insufficient Public Data" or "Not Public"
- **Deterministic output** — Low temperature (0.2) and controlled top_p (0.9) reduce randomness
- **Structured format** — Every section has explicit format requirements

### Modifying the Prompt

To change the analysis requirements, edit the `SYSTEM_PROMPT` constant in `services/analyzer.py`. Key areas you can customize:

- Section word limits (e.g., Executive Summary: 120-150 words)
- SWOT bullet count (currently 3-5 per quadrant)
- Risk scale definition
- Additional sections

---

## Error Handling

| Scenario                    | User-facing behavior                                 |
|-----------------------------|------------------------------------------------------|
| Empty company name          | 400 error: "Company name is required"                |
| Company name too long       | 400 error: "Company name too long"                   |
| Groq API key missing        | 400 error: "GROQ_API_KEY environment variable not set" |
| All LLM models fail         | 502 error: "Analysis failed: All models failed."     |
| DuckDuckGo search fails     | Graceful fallback — analysis continues with limited data |
| Invalid JSON from LLM       | Retry with fallback model; regex JSON extraction as last resort |
| Network/server error        | 500 error: "An unexpected error occurred."           |

---

## Customization Guide

### Changing the LLM Model

Edit `services/analyzer.py`, line with the `models` list:

```python
models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
```

Replace with any Groq-supported model.

### Changing the Port

Set the `PORT` environment variable in `.env`:

```
PORT=3000
```

### Adding More Search Sources

Edit `services/search.py` to add additional search queries or integrate other APIs (e.g., SerpAPI, Google Custom Search).

### Styling Changes

All styles are in `static/style.css` using CSS custom properties. Key tokens to modify:

```css
--blue-600: #2563eb;    /* Primary accent */
--gray-50: #f9fafb;     /* Page background */
--white: #ffffff;        /* Card background */
```

---

## Deployment

### Docker (recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

```bash
docker build -t bi-assist .
docker run -p 8000:8000 --env-file .env bi-assist
```

### Railway / Render / Fly.io

1. Push the repo to GitHub
2. Connect the repo to your deployment platform
3. Set the `GROQ_API_KEY` environment variable
4. Set the start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Environment Variables for Production

| Variable        | Value                     |
|----------------|---------------------------|
| `GROQ_API_KEY` | Your production API key   |
| `PORT`         | Platform-assigned port    |

---

## Troubleshooting

| Problem                                 | Solution                                                        |
|-----------------------------------------|-----------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt`                   |
| `GROQ_API_KEY environment variable not set`     | Create a `.env` file with your key                      |
| Analysis takes too long (>60s)          | This is normal for the first request; Groq cold starts can be slow |
| `429 Too Many Requests` from Groq       | You've hit the rate limit; wait and retry                |
| DuckDuckGo search returns empty results | DuckDuckGo may be rate-limiting; try again after a few minutes  |
| Port 8000 already in use                | Change the port in `.env` or kill the process using that port   |
| JSON parse error in frontend            | Check browser console; the LLM may have returned invalid JSON   |

---

## License

This project is open source. See the repository for license details.
