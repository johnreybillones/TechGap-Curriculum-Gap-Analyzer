# TechGap Curriculum Gap Analyzer

TechGap is a web application that compares academic curriculum skills with job-market skill requirements.
It helps identify matched skills, missing skills, and overall curriculum-job alignment to support curriculum improvement decisions.

## Results You Get

After selecting a curriculum and a job role, TechGap returns actionable outputs:

- **Curriculum-job alignment score** to quickly see fit against industry demand.
- **Skill coverage metrics** showing how much of the target role is currently covered.
- **Matched skills list** to highlight strengths already present in the curriculum.
- **Missing skill list** to reveal concrete competency gaps.
- **Priority insights via charts** to make high-impact gaps easier to identify.
- **Recommendation text** that translates analysis findings into improvement suggestions.

## Core Features

- Analyze curriculum vs job-role requirements in a single workflow.
- Surface measurable outputs (coverage, relevance, and alignment indicators).
- Present both summary KPIs and detailed skill-level breakdowns.
- Support evidence-based curriculum updates using gap-focused recommendations.

## Quick Start

### 1) Frontend (React + Vite)

```bash
npm install
npm run dev
```

### 2) Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

## How to Use

1. Open the web app.
2. Choose a curriculum.
3. Choose a job role.
4. Run analysis.
5. Review alignment score, coverage metrics, matched skills, and missing skills.
6. Use the generated recommendations as input for curriculum enhancement planning.