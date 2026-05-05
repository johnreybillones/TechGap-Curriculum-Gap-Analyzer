# TechGap — Curriculum Gap Analyzer

> An AI-powered web application that identifies skill gaps between academic curricula and real-world job market demands.

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.x-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Vite](https://img.shields.io/badge/Vite-7.x-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Environment Variables](#2-environment-variables)
  - [3. Backend Setup](#3-backend-setup)
  - [4. Frontend Setup](#4-frontend-setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Supported Curriculum Tracks](#supported-curriculum-tracks)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**TechGap** is a full-stack curriculum gap analysis tool designed for academic institutions, curriculum designers, and educators. It compares the skills embedded in a course program against the skill requirements extracted from real-world job postings, surfacing actionable insights to help bridge the gap between academic training and industry expectations.

By combining semantic similarity (via embeddings and scikit-learn), a MySQL-backed skill database, and Google Generative AI for recommendations, TechGap turns raw curriculum data into prioritized, evidence-based improvement plans.

---

## Features

| Feature | Description |
|---|---|
| 📊 **Alignment Score** | An overall curriculum-to-job-role fit score |
| 📈 **Coverage Metrics** | Percentage of required job skills covered by the curriculum |
| ✅ **Matched Skills** | Skills present in both the curriculum and the job role |
| ❌ **Missing Skills** | Critical skill gaps absent from the curriculum |
| 🤖 **AI Recommendations** | Google Gemini-generated improvement suggestions |
| 📉 **Interactive Charts** | Visual breakdown of skill distribution and gaps via Recharts |
| 🌙 **Dark Mode** | Toggleable dark/light theme with persistent preference |
| ⚡ **Cache Warming** | Background startup cache for faster first-request response |

---

## Tech Stack

### Frontend
- **React 19** — UI component framework
- **Vite 7** — Development server and build tool
- **Tailwind CSS 4** — Utility-first styling
- **Recharts** — Chart visualizations
- **Lucide React** — Icon library
- **React Markdown** — Renders AI recommendation text

### Backend
- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM for database access
- **MySQL** — Relational database
- **Pydantic** — Data validation and schemas
- **Uvicorn** — ASGI server
- **scikit-learn / PyTorch** — Skill similarity and ML prediction
- **Google Generative AI (Gemini)** — AI-generated curriculum recommendations
- **python-dotenv** — Environment variable management

---

## Project Structure

```
TechGap-Curriculum-Gap-Analyzer/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/                # API route handlers
│   │   ├── core/               # App configuration and settings
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── services/           # Business logic layer
│   │   ├── database.py         # DB session and engine setup
│   │   ├── main.py             # FastAPI app entry point
│   │   └── models.py           # SQLAlchemy ORM models
│   ├── routers/                # Legacy/additional route modules
│   ├── model/                  # Saved ML model artifacts
│   ├── csvs/                   # Seed/import data (CSV)
│   ├── requirements.txt        # Python dependencies
│   └── get_cert_path.py        # SSL cert utility
├── src/                        # React frontend
│   ├── components/
│   │   ├── analyzer/           # Core analysis UI components
│   │   │   ├── ControlPanel    # Program/career selectors + Analyze button
│   │   │   ├── MetricsGrid     # KPI score cards
│   │   │   ├── AIRecommendations # Collapsible AI suggestion panel
│   │   │   └── SkillDetails    # Matched/missing skill lists
│   │   ├── charts/             # Recharts visualizations
│   │   └── layout/             # Header, Footer, Background
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAnalysis.js      # Analysis state and API calls
│   │   ├── useOptions.js       # Program/career dropdown data
│   │   └── useDarkMode.js      # Dark mode persistence
│   ├── utils/                  # Shared utilities
│   ├── App.jsx                 # Root application component
│   └── main.jsx                # React entry point
├── public/                     # Static assets
├── index.html                  # HTML shell
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
├── package.json                # Node.js dependencies
└── .env                        # Frontend environment variables
```

---

## Prerequisites

Ensure you have the following installed:

| Tool | Version |
|---|---|
| Node.js | 18+ |
| npm | 9+ |
| Python | 3.10+ |
| MySQL | 8.0+ |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/johnreybillones/TechGap-Curriculum-Gap-Analyzer.git
cd TechGap-Curriculum-Gap-Analyzer
```

### 2. Environment Variables

**Frontend** — create or update the root `.env` file:

```env
# .env (project root)
VITE_API_URL=http://127.0.0.1:8000
```

**Backend** — create `backend/app/.env`:

```env
# backend/app/.env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=techgap_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password

GOOGLE_API_KEY=your_google_generative_ai_key
```

> **Note:** Never commit `.env` files containing credentials. They are already listed in `.gitignore`.

---

### 3. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload
```

The API will be available at: **`http://127.0.0.1:8000`**

Interactive API docs: **`http://127.0.0.1:8000/docs`**

---

### 4. Frontend Setup

```bash
# From the project root
npm install
npm run dev
```

The app will be available at: **`http://localhost:5173`**

---

## Usage

1. Open the application in your browser.
2. **Select a Curriculum** — Choose an academic program track from the dropdown.
3. **Select a Job Role** — Choose the target industry job role to compare against.
4. **Click "Analyze"** — The system computes the gap analysis.
5. **Review Results:**
   - **Alignment Score** — Overall fit between curriculum and job role.
   - **Coverage Metrics** — How much of the job's required skills are covered.
   - **Charts** — Visual breakdown of matched, partial, and missing skills.
   - **AI Recommendations** — Gemini-generated suggestions for curriculum improvement.
   - **Skill Details** — Full lists of matched and missing skills.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/options` | Fetch available curricula and job roles |
| `POST` | `/gap-analysis` | Run gap analysis for a curriculum/job pair |
| `GET` | `/curriculum` | List all curricula |
| `GET` | `/job-role` | List all job roles |
| `GET` | `/skill` | List all skills |
| `POST` | `/predict` | ML-based skill match prediction |
| `GET` | `/gap-report` | Retrieve stored gap reports |
| `GET` | `/match-result` | Retrieve stored match results |

> Full interactive documentation is available at `http://127.0.0.1:8000/docs` when the backend is running.

---

## Database Schema

The application uses a relational MySQL database with the following core tables:

```
curriculum          — Academic programs with course info and track
job_role            — Industry job roles with descriptions
skill               — Normalized skill vocabulary
course_skill        — Many-to-many: curriculum ↔ skill
job_skill           — Many-to-many: job_role ↔ skill
embedding           — Stored vector embeddings for curricula, jobs, and skills
match_result        — Computed alignment scores per curriculum/job pair
skill_match_detail  — Per-skill similarity scores (match / partial / gap)
gap_report          — Stored recommendations and identified missing skills
```

---

## Supported Curriculum Tracks

| Track |
|---|
| CS — Intelligent Systems |
| CS — Game Development |
| IT — Web Development |
| IT — Network Technology |
| Other |

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## License

This project is intended for academic and educational purposes.