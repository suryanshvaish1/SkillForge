# SkillForge — Adaptive Learning Engine

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)

> **AI-powered skill gap analysis and personalised learning pathway generator for corporate onboarding and talent development.**

## Live Demo

**https://skill-forge-three-blue.vercel.app/**


SkillForge ingests a candidate's resume and a target job description, identifies exact skill gaps using NLP and semantic similarity, and produces a phased, prerequisite-aware learning pathway grounded entirely in a curated course catalog — with zero hallucination.

## Screenshots
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4c6c352d-778e-4d07-b564-a9381318bc10" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f2734f5e-7ba0-469e-96b6-1b6e7b31e0a8" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/76ed0242-59b8-4242-94d8-0b69d4e0bd85" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/086c10b7-3804-4d08-be28-041536fe3d16" />

## Video Demo
**https://youtu.be/6DGx2sHHAZw**

---

## Table of Contents

- [Live Demo](#-live-demo)
- [Quick Start](#-quick-start)
- [Overview](#overview)
- [Sample Test Files](#-sample-test-files)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Logic: Skill-Gap Analysis Pipeline](#logic-skill-gap-analysis-pipeline)
- [Dependencies](#dependencies)
- [Setup & Installation](#setup--installation)
  - [Option A — Docker (Recommended)](#option-a--docker-recommended)
  - [Option B — Local Development](#option-b--local-development)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Course Catalog](#course-catalog)
  

---

## Quick Start

Get started in under a minute:

1. Open the **Live Demo**.
2. Upload a sample resume from `sample_resumes/`.
3. Upload a sample job description from `sample_jds/`.
4. Click **Analyze**.
5. Explore the extracted skills, skill gaps, adaptive learning pathway and reasoning trace.

---

## Overview

Traditional corporate training is one-size-fits-all. SkillForge solves this by:

1. **Parsing** resumes and job descriptions from PDF, DOCX, or plain text
2. **Extracting** skills using a hand-crafted taxonomy of 80+ canonical skills with 300+ aliases, augmented by spaCy NER
3. **Analysing gaps** using level-aware comparison and sentence-transformer semantic matching
4. **Generating pathways** through a prerequisite DAG (directed acyclic graph) with TF-IDF course scoring and topological phase ordering
5. **Presenting results** in an interactive React dashboard with full reasoning transparency

---

## System Architecture

<img width="1830" height="757" alt="image" src="https://github.com/user-attachments/assets/eb6bb2a3-e472-4979-b892-659c9e3d12ed" />


> **Docker Compose** orchestrates the backend (port 8000) and frontend (port 80) containers with a health-check dependency and a shared nginx reverse proxy.

---

## Features

| Feature | Description |
|---|---|
| **Multi-format ingestion** | PDF (pdfplumber + PyPDF2 fallback), DOCX, TXT, or direct paste |
| **Taxonomy matching** | 80+ canonical skills, 300+ aliases, regex-based with word boundary guards |
| **spaCy NER augmentation** | ORG/PRODUCT entity extraction catches skills missed by taxonomy |
| **Level inference** | Detects BEGINNER → EXPERT from surrounding context (sentence-scoped) |
| **Years extraction** | Regex extracts `N years of experience` from surrounding sentences |
| **Semantic gap matching** | `all-MiniLM-L6-v2` cosine similarity bridges alias variations (threshold 0.65) |
| **Priority scoring** | Gap score → CRITICAL / HIGH / MEDIUM / LOW priority bands |
| **Graph-based pathing** | NetworkX DAG with transitive prerequisite resolution |
| **Weighted set cover** | Selects minimal course set covering all gaps |
| **Mastery filtering** | Skips courses where candidate already knows ≥90% of content |
| **Phased output** | Topological sort → Foundation / Core Development / Advanced / Capstone phases |
| **Reasoning trace** | Every pipeline step logged with data payload for transparency |
| **Cross-domain** | Technical, management, soft skills, and operational/labour roles |
| **Live Deployment** | Hosted on Vercel for instant access |
| **Sample Test Files** | Includes sample resumes and job descriptions for quick evaluation |

---

## Tech Stack

### Backend
| Library | Version | Role |
|---|---|---|
| FastAPI | 0.104.1 | REST API framework |
| Uvicorn | 0.24.0 | ASGI server |
| Pydantic v2 | 2.5.2 | Schema validation |
| spaCy | 3.7.2 | NLP / NER (`en_core_web_sm`) |
| sentence-transformers | 2.2.2 | Semantic similarity embeddings |
| scikit-learn | 1.3.2 | TF-IDF vectoriser, cosine similarity |
| NetworkX | 3.2.1 | Prerequisite DAG, topological sort |
| pdfplumber | 0.10.3 | PDF text extraction |
| PyPDF2 | 3.0.1 | PDF fallback extractor |
| python-docx | 1.1.0 | DOCX extraction |
| loguru | 0.7.2 | Structured logging |
| PyTorch (CPU) | latest | Sentence-transformer backend |

### Frontend
| Library | Version | Role |
|---|---|---|
| React | 18.2.0 | UI framework |
| Vite | 5.0.8 | Build tool & dev server |
| Tailwind CSS | 3.4.0 | Utility-first styling |
| framer-motion | 10.16.16 | Animations |
| lucide-react | 0.294.0 | Icon set |

### Infrastructure
| Tool | Role |
|---|---|
| Docker + Docker Compose | Container orchestration |
| nginx (alpine) | Frontend static server + API reverse proxy |
| Python 3.11-slim | Backend base image |

---

## Project Structure

```
skillforge/
├── sample_resumes/      # Sample resumes
├── sample_jds/          # Sample job descriptions
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # POST /analyse, GET /health, GET /catalog/stats
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic settings (env-driven)
│   │   │   └── logger.py          # Loguru setup (console + rotating file)
│   │   ├── data/
│   │   │   └── course_catalog.json  # 60+ courses across 11 domains
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models: ExtractedSkill, SkillGap, etc.
│   │   ├── services/
│   │   │   ├── skill_extractor.py   # NLP skill extraction pipeline
│   │   │   ├── gap_analyser.py      # Level-aware gap computation
│   │   │   └── pathway_generator.py # Graph-based adaptive pathway
│   │   ├── utils/
│   │   │   └── text_extraction.py   # PDF / DOCX / TXT parsing
│   │   └── main.py                # FastAPI app factory + lifespan hooks
│   ├── test/
│   │   └── test_engine.py         # pytest suite (unit + integration)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── FileUploader.jsx   # File drop + paste text modes
│   │   │   ├── SkillsPanel.jsx    # Extracted skills with level chips
│   │   │   ├── GapPanel.jsx       # Priority-ordered gap bars
│   │   │   ├── PathwayView.jsx    # Phased timeline + course cards
│   │   │   ├── ReasoningTrace.jsx # Step-by-step pipeline transparency
│   │   │   └── LoadingState.jsx
│   │   ├── hooks/
│   │   │   └── useAnalysis.js     # Async API state management
│   │   ├── utils/
│   │   │   └── api.js             # fetch wrapper for /api/v1
│   │   ├── styles/
│   │   │   └── globals.css        # Tailwind layers + custom components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── nginx.conf
│   ├── Dockerfile
│   ├── package.json
│   └── tailwind.config.js
└── docker-compose.yml
```

---

## Logic: Skill-Gap Analysis Pipeline

The pipeline runs in five sequential stages. Each stage appends a step to the `reasoning_trace` returned in the API response.

### Stage 1 — Document Parsing

`app/utils/text_extraction.py`

Files are routed by extension:
- `.pdf` → pdfplumber (page-by-page); falls back to PyPDF2 on error
- `.docx` / `.doc` → python-docx paragraph extraction
- `.txt` / `.md` → UTF-8 decode

Both resume and JD are capped at **10 MB**. Extracted text is passed as plain strings to Stage 2.

---

### Stage 2 — Skill Extraction

`app/services/skill_extractor.py`

**Step 2a: Taxonomy Matching (Primary)**

A hand-crafted `SKILL_TAXONOMY` dict maps 80+ canonical skill names to sets of known aliases:

```python
"apache kafka": {"kafka", "apache kafka"},
"power bi": {"power bi", "powerbi", "power-bi", "dax"},
```

For each alias, a regex is compiled:
- Short aliases (≤2 chars, e.g. `"r"`, `"go"`): strict `\b` word boundaries
- Longer aliases: lookahead/lookbehind `(?<![a-z])...(? (?![a-z])` to handle camelCase and compound words

On the first match, the surrounding sentence is extracted (bounded by `.` or `\n`) and passed to level inference.

**Step 2b: Level Inference**

`_infer_level()` searches the sentence window (±150 chars, sentence-bounded) for level keywords:

| Level | Keywords (sample) |
|---|---|
| BEGINNER | basic, fundamentals, familiar, exposure, 0-1 year |
| INTERMEDIATE | proficient, hands-on, 2-3 years, solid, working knowledge |
| ADVANCED | senior, extensive, 5+ years, strong, thorough |
| EXPERT | expert, architect, principal, 10+ years, thought leader |

**Step 2c: Years Extraction**

`_infer_years()` applies two regex patterns in the sentence window:
- `(\d+)+?\s*(?:years?|yrs?)...`
- `(?:experience|exp)\s*(?:of\s*)?(\d+)+?\s*(?:years?|yrs?)`

**Step 2d: spaCy NER (Supplementary)**

The first 5000 chars are passed to `en_core_web_sm`. Any `ORG` or `PRODUCT` entity whose lowercased text appears in the alias index is added as a skill (level=NONE) if not already found by taxonomy.

Deduplication is enforced — each canonical skill appears at most once per document.

---

### Stage 3 — Gap Analysis

`app/services/gap_analyser.py`

**Level Scoring**

Each `SkillLevel` maps to a numeric score:

```
NONE=0.0, BEGINNER=0.25, INTERMEDIATE=0.5, ADVANCED=0.75, EXPERT=1.0
```

JD skills with no explicit level default to `INTERMEDIATE`.

**Matching Strategy**

For each JD skill:
1. **Exact match** — look up the lowercased skill name in the resume skill map
2. **Semantic match** — if no exact match, use `all-MiniLM-L6-v2` (sentence-transformers) to compute cosine similarity between all JD skill names and all resume skill names. A match is accepted at similarity ≥ **0.65**

**Gap Computation**

```
gap_score = max(0, required_level_score − current_level_score)
```

A threshold of 0.05 is applied to avoid noise from rounding. Gaps are sorted descending by `gap_score`.

**Priority Bands**

```
gap_score ≥ 0.70 → CRITICAL
gap_score ≥ 0.50 → HIGH
gap_score ≥ 0.25 → MEDIUM
gap_score  < 0.25 → LOW
```

Skills where `gap_score ≤ 0.05` (candidate meets or exceeds requirement) are added to the `already_met` list.

---

### Stage 4 — Pathway Generation

`app/services/pathway_generator.py`

**4a: Course Scoring (TF-IDF)**

All gap skill names are concatenated into a single query string. A TF-IDF vectoriser (500 features, English stop words) transforms it and computes cosine similarity against all course corpus strings (skills + description).

Boosting rules applied per course:
- `+0.3` per directly overlapping skill (gap name ∈ `skills_covered`)
- `+0.2` for each CRITICAL gap skill covered
- `+0.1` for each HIGH gap skill covered

**4b: Weighted Set Cover**

Courses are iterated in descending relevance order. A course is selected if it covers at least one uncovered gap skill. This continues until all gaps are covered or the list is exhausted.

**4c: Prerequisite Resolution**

Starting from the selected set, a BFS traverses the prerequisite DAG (built from `course_catalog.json`). A prerequisite is only added if the candidate doesn't already know ≥ **80%** of its covered skills (mastery ratio check).

**4d: Mastery Filtering**

A final pass removes any course where the candidate already knows ≥ **90%** of its `skills_covered` content (based on resume skills + `already_met`).

**4e: Topological Phasing**

NetworkX `topological_generations()` groups courses into dependency layers. These map to named phases:

| Generation | Phase Name |
|---|---|
| 0 | Foundation |
| 1 | Core Development |
| 2 | Advanced Specialisation |
| 3+ | Capstone |

Within each phase, courses are sorted by `relevance_score` descending. A fallback groups by difficulty (beginner → intermediate → advanced) if the DAG contains cycles.

**4f: Summary**

Total hours, estimated weeks (at 10h/week), domain coverage breakdown, and top-5 gaps by score are computed from the final phase set.

---

### Stage 5 — Response Assembly

`app/api/routes.py`

All pipeline outputs are assembled into `AnalysisResponse`:

```json
{
  "resume_skills":   [...],    // ExtractedSkill[]
  "jd_skills":       [...],    // ExtractedSkill[]
  "skill_gaps":      [...],    // SkillGap[] sorted by gap_score desc
  "pathway":         [...],    // PathwayPhase[] ordered by phase_number
  "summary":         {...},    // PathwaySummary
  "reasoning_trace": [...]     // ReasoningStep[] — full audit trail
}
```

---

## Dependencies

### Python (backend/requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.2
PyPDF2==3.0.1
python-docx==1.1.0
pdfplumber==0.10.3
torch          # CPU build via --extra-index-url
torchvision
torchaudio
spacy==3.7.2
scikit-learn==1.3.2
sentence-transformers==2.2.2
numpy==1.26.2
networkx==3.2.1
loguru==0.7.2
pytest==7.4.3
pytest-asyncio==0.23.2
starlette==0.27.0
```

spaCy model installed separately:
```
en_core_web_sm-3.7.1
```

### Node.js (frontend/package.json)

```json
"dependencies": {
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "lucide-react": "^0.294.0",
  "framer-motion": "^10.16.16"
},
"devDependencies": {
  "@vitejs/plugin-react": "^4.2.1",
  "tailwindcss": "^3.4.0",
  "autoprefixer": "^10.4.16",
  "postcss": "^8.4.32",
  "vite": "^5.0.8"
}
```

---

## Setup & Installation

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 24+ (or Docker Engine + Compose v2)
- Git

---

### Option A — Docker (Recommended)

This is the simplest path and guaranteed to reproduce the exact environment.

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/skillforge.git
cd skillforge

# 2. Build and start all services
docker compose up --build

# 3. Open in your browser
#    Frontend:  http://localhost
#    API docs:  http://localhost:8000/docs
#    Health:    http://localhost:8000/api/v1/health
```

> **First build note:** The backend image downloads PyTorch (CPU), spaCy, and sentence-transformers. Allow ~5–10 minutes on first build depending on your connection. Subsequent builds use Docker layer cache.

To run in detached mode:
```bash
docker compose up --build -d
docker compose logs -f backend   # stream backend logs
```

To stop:
```bash
docker compose down
```

---

### Option B — Local Development

#### Backend

```bash
# 1. Create and activate virtual environment
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 2. Install PyTorch CPU build first (avoids pulling CUDA binaries)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Install remaining dependencies
pip install -r requirements.txt

# 4. Install spaCy language model
python -m spacy download en_core_web_sm

# 5. Copy and review environment config
cp .env .env.local   # edit if needed

# 6. Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```


#### Frontend

```bash
# In a new terminal
cd frontend

# Install Node dependencies (Node 18+ required)
npm install

# Start dev server (proxies /api to localhost:8000)
npm run dev
```

Frontend available at: `http://localhost:3000`

#### Build Frontend for Production

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

---

## API Reference

### `POST /api/v1/analyse`

Accepts `multipart/form-data`.

| Field | Type | Description |
|---|---|---|
| `resume_file` | File | Resume as PDF, DOCX, or TXT (max 10 MB) |
| `resume_text` | string | Resume as plain text (alternative to file) |
| `jd_file` | File | Job description file (max 10 MB) |
| `jd_text` | string | Job description as plain text (alternative to file) |

At least one of `resume_file`/`resume_text` or `jd_file`/`jd_text` must be provided.

**Response** `200 OK`

```json
{
  "resume_skills": [
    { "name": "python", "level": "advanced", "years_experience": 5, "context": "..." }
  ],
  "jd_skills": [...],
  "skill_gaps": [
    { "skill": "machine learning", "current_level": "none", "required_level": "intermediate",
      "gap_score": 0.5, "priority": "high" }
  ],
  "pathway": [
    {
      "phase_name": "Foundation",
      "phase_number": 1,
      "description": "...",
      "courses": [
        { "id": "DS-101", "title": "Statistics & Probability Foundations",
          "difficulty": "beginner", "duration_hours": 25, "relevance_score": 0.72,
          "reason": "Addresses 'statistics' gap (high priority)", ... }
      ],
      "total_hours": 47,
      "skills_addressed": [...]
    }
  ],
  "summary": {
    "total_courses": 6,
    "total_hours": 150,
    "estimated_weeks": 15.0,
    "phases": 3,
    "top_gaps": ["machine learning", "deep learning", "nlp"],
    "skills_already_met": ["python", "docker", "sql"],
    "domain_coverage": { "technical": 5, "business": 1 }
  },
  "reasoning_trace": [
    { "step": 0, "action": "Document Parsing", "detail": "...", "data": {...} },
    ...
  ]
}
```

---

### `GET /api/v1/health`

```json
{ "status": "healthy", "service": "adaptive-learning-engine" }
```

### `GET /api/v1/catalog/stats`

```json
{
  "total_courses": 63,
  "domains": { "technical": 42, "management": 3, "soft_skills": 3, "operational": 6, "business": 4 },
  "prerequisite_edges": 28
}
```

---

##  Sample Test Files

The repository includes ready-to-use test documents.

```
sample_resumes/
sample_jds/
```

Use these files to quickly evaluate:

- Resume parsing
- Job description parsing
- Skill extraction
- Skill gap analysis
- Adaptive learning pathway generation
- Reasoning trace visualization

You can also upload your own PDF, DOCX or TXT resumes and job descriptions.

---

## Usage

SkillForge supports two input methods:

- Upload Resume + Job Description files
- Paste resume and JD text directly

After clicking **Analyze**, the application generates:

- Extracted Skills
- Skill Gap Analysis
- Priority Ranking
- Personalized Learning Pathway
- Complete AI Reasoning Trace

---

## Running Tests

```bash
cd backend

# Run all tests (requires virtual environment to be active)
pytest test/test_engine.py -v --tb=short

# Run specific test class
pytest test/test_engine.py::TestSkillExtractor -v
pytest test/test_engine.py::TestGapAnalyser -v
pytest test/test_engine.py::TestPathwayGenerator -v
pytest test/test_engine.py::TestAPIEndpoints -v
```

The test suite covers:
- Skill extraction accuracy (resume + JD + operational text)
- Deduplication and empty input handling
- Level inference and years extraction
- Gap identification, ordering, and edge cases
- Prerequisite resolution in the pathway generator
- Cross-domain scalability (operational/labour roles)
- All three REST endpoints via FastAPI `TestClient`

---

## Configuration

Backend configuration is driven by `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `AdaptiveLearnEngine` | Application name |
| `APP_ENV` | `development` | Environment tag |
| `APP_DEBUG` | `true` | Enables detailed error diagnostics |
| `LOG_LEVEL` | `DEBUG` | Loguru log level |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed frontend origins |
| `HOST` | `0.0.0.0` | Uvicorn bind host |
| `PORT` | `8000` | Uvicorn bind port |
| `SPACY_MODEL` | `en_core_web_sm` | spaCy model identifier |
| `COURSE_CATALOG_PATH` | `data/course_catalog.json` | Relative path to catalog |

Docker Compose overrides `APP_ENV=production`, `APP_DEBUG=false`, `LOG_LEVEL=INFO`.

---

## Course Catalog

`backend/app/data/course_catalog.json` defines all available courses. To add courses:

```json
{
  "id": "YOUR-001",
  "title": "Your Course Title",
  "description": "Brief description of what students will learn.",
  "skills_covered": ["skill-a", "skill-b"],
  "difficulty": "beginner|intermediate|advanced",
  "duration_hours": 20,
  "prerequisites": ["EXISTING-001"],
  "domain": "technical|management|soft_skills|operational|business"
}
```

Add the entry under the appropriate category key. The prerequisite graph and TF-IDF index are rebuilt automatically on startup.

**Current catalog coverage:**

| Domain | Courses | Sample Skills |
|---|---|---|
| Programming | 8 | Python, Java, TypeScript, Go, Rust |
| Data Engineering | 7 | SQL, Kafka, Spark, Airflow, dbt |
| Data Science | 7 | ML, Deep Learning, NLP, Pandas, A/B Testing |
| Web Development | 6 | React, Node.js, Next.js, GraphQL, Angular |
| DevOps & Cloud | 9 | Docker, Kubernetes, AWS, Terraform, CI/CD |
| Security | 3 | AppSec, OWASP, Cloud Security |
| Project Management | 3 | Agile, Scrum, TPM |
| Soft Skills | 3 | Technical Writing, Leadership |
| Operations | 6 | Warehouse, Supply Chain, CNC, Forklift |
| Business Analytics | 4 | Power BI, Tableau, Excel, Business Analysis |
| AI/ML Engineering | 3 | MLOps, LLM Development, Computer Vision |

---

## Future Enhancements

- Resume scoring against multiple job descriptions
- Export learning pathways as PDF
- User authentication
- Learning progress tracking
- LMS integration
- LLM-powered course recommendations
- Multi-language resume support

---

## Acknowledgements

Built with FastAPI, spaCy, sentence-transformers, NetworkX, React, and Tailwind CSS.

---

