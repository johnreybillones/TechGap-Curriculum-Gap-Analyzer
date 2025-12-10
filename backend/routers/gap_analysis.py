import os
from dotenv import load_dotenv

from datetime import date
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database import SessionLocal

# Load .env from app directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')
load_dotenv(dotenv_path)
from app.models import (
    Curriculum,
    GapReport,
    JobRole,
    JobSkill,
    CourseSkill,
    MatchResult,
    Skill,
    SkillMatchDetail,
)

router = APIRouter(tags=["Gap Analysis"])

# In-memory caches
_OPTIONS_CACHE = None

# --- CONFIGURATION: JOBS TO HIDE ---
BLACKLIST_JOBS = {
    "statistics",
    "business analyst",
    "data warehousing",
    "technology integration",
    "technical operations"
}

# -----------------------
# Helpers
# -----------------------
def invalidate_options_cache():
    global _OPTIONS_CACHE
    _OPTIONS_CACHE = None

def normalize_string(text: str) -> str:
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

# -----------------------
# Dependencies & Schemas
# -----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class GapAnalysisBase(BaseModel):
    course_id: int
    missing_skill_id: int
    recommendation: Optional[str] = None
    date_generated: Optional[date] = None

class GapAnalysisCreate(GapAnalysisBase):
    pass

class GapAnalysisOut(GapAnalysisBase):
    report_id: int
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    curriculum_id: int
    job_id: int


# -----------------------
# CORE LOGIC (DB Only)
# -----------------------

def _calculate_gap_analysis(curriculum_id: int, job_id: int, db: Session):
    # 1. Fetch Entities
    curriculum = db.query(Curriculum).filter(Curriculum.curriculum_id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail=f"Curriculum {curriculum_id} not found")

    job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

    # 2. Metrics Denominator: Total Skills in Curriculum
    total_curriculum_skills = db.query(func.count(CourseSkill.skill_id))\
        .filter(CourseSkill.curriculum_id == curriculum_id)\
        .scalar() or 0

    matches = []
    gaps = []
    
    # 3. Query SkillMatchDetail (Single Source of Truth)
    db_details = db.query(SkillMatchDetail, Skill.skill_name)\
        .join(Skill, SkillMatchDetail.skill_id == Skill.skill_id)\
        .filter(
            SkillMatchDetail.curriculum_id == curriculum_id,
            SkillMatchDetail.job_id == job_id
        ).all()

    # 4. Process Results
    if db_details:
        for row, skill_name in db_details:
            if row.status == 'match':
                matches.append(skill_name)
            else:
                gaps.append(skill_name)

    # 5. Calculate Metrics
    matches = sorted(list(set(matches)))
    gaps = sorted(list(set(gaps)))
    
    match_count = len(matches)
    gap_count = len(gaps)
    
    total_job_needs = match_count + gap_count
    
    # Avoid division by zero
    if total_curriculum_skills == 0:
        total_curriculum_skills = match_count if match_count > 0 else 1

    # Logic for Curriculum Relevance (Option B):
    # Relevance = (Skills Matched / Total Curriculum Skills)
    # Irrelevant = (Total Curriculum Skills - Skills Matched)
    irrelevant_count = max(0, total_curriculum_skills - match_count)

    coverage = (match_count / total_job_needs) if total_job_needs > 0 else 0.0
    relevance = (match_count / total_curriculum_skills) if total_curriculum_skills > 0 else 0.0
    if relevance > 1.0: relevance = 1.0
    
    return {
        "coverage": f"{coverage * 100:.1f}%",
        "relevance": f"{relevance * 100:.1f}%",
        "coverage_score": round(coverage * 100, 1),
        "relevance_score": round(relevance * 100, 1),
        
        # Counts
        "matchingSkills": match_count,
        "missingSkills": gap_count,
        "totalCurriculumSkills": total_curriculum_skills,
        "irrelevantSkills": irrelevant_count,
        
        # Detailed Lists
        "exact": matches,
        "gaps": gaps
    }


# -----------------------
# Analysis Endpoints
# -----------------------
@router.post("/api/analyze")
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    return _calculate_gap_analysis(request.curriculum_id, request.job_id, db)


# -----------------------
# Filtered Options Endpoint
# -----------------------
@router.get("/api/options")
def get_options(db: Session = Depends(get_db)):
    global _OPTIONS_CACHE
    if _OPTIONS_CACHE is not None:
        return _OPTIONS_CACHE

    # SUPER OPTIMIZED: Use pre-computed summary table (avoids 6M+ row scans)
    try:
        from sqlalchemy import text
        
        # Try to use summary table first (much faster)
        curricula_query = text("""
            SELECT entity_id as id, label 
            FROM options_summary 
            WHERE entity_type = 'curriculum'
            ORDER BY entity_id
        """)
        jobs_query = text("""
            SELECT entity_id as id, label 
            FROM options_summary 
            WHERE entity_type = 'job'
            ORDER BY entity_id
        """)
        
        curricula_rows = db.execute(curricula_query).fetchall()
        jobs_rows = db.execute(jobs_query).fetchall()
        
        # Deduplicate and filter
        curriculum_options = []
        seen_c = set()
        for row in curricula_rows:
            label = row.label or ""
            norm = normalize_string(label)
            if norm and norm not in seen_c:
                curriculum_options.append({"id": row.id, "label": label})
                seen_c.add(norm)
        
        job_options = []
        seen_j = set()
        for row in jobs_rows:
            label = row.label or ""
            if label.lower().strip() in BLACKLIST_JOBS:
                continue
            norm = normalize_string(label)
            if norm and norm not in seen_j:
                job_options.append({"id": row.id, "label": label})
                seen_j.add(norm)
        
        _OPTIONS_CACHE = {"curricula": curriculum_options, "jobs": job_options}
        return _OPTIONS_CACHE
        
    except Exception as e:
        # Fallback to JOIN query if summary table doesn't exist
        print(f"⚠️ Summary table not found, using slow fallback: {e}")
        
        curricula = db.query(Curriculum)\
            .join(SkillMatchDetail, Curriculum.curriculum_id == SkillMatchDetail.curriculum_id)\
            .distinct()\
            .order_by(Curriculum.curriculum_id)\
            .all()
        
        jobs = db.query(JobRole)\
            .join(SkillMatchDetail, JobRole.job_id == SkillMatchDetail.job_id)\
            .distinct()\
            .order_by(JobRole.job_id)\
            .all()

        curriculum_options = []
        seen_c = set()
        for c in curricula:
            label = c.track or c.course_title or ""
            norm = normalize_string(label)
            if norm and norm not in seen_c:
                curriculum_options.append({"id": c.curriculum_id, "label": label})
                seen_c.add(norm)
        
        job_options = []
        seen_j = set()
        for j in jobs:
            label = j.query or j.title or ""
            if label.lower().strip() in BLACKLIST_JOBS:
                continue
            norm = normalize_string(label)
            if norm and norm not in seen_j:
                job_options.append({"id": j.job_id, "label": label})
                seen_j.add(norm)

        _OPTIONS_CACHE = {"curricula": curriculum_options, "jobs": job_options}
        return _OPTIONS_CACHE

# ... (Keep the Debug and CRUD endpoints below this line exactly as they were in your file)


# -----------------------
# Debug Endpoint
# -----------------------
@router.get("/api/debug/full_matrix")
def debug_full_matrix(db: Session = Depends(get_db)):
    print("\n" + "="*80)
    print(f"{'FULL MATRIX GAP ANALYSIS (Strict DB)':^80}")
    print("="*80 + "\n")
    
    active_c_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.curriculum_id)).all()]
    active_j_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.job_id)).all()]

    curricula = db.query(Curriculum).filter(Curriculum.curriculum_id.in_(active_c_ids)).all()
    jobs = db.query(JobRole).filter(JobRole.job_id.in_(active_j_ids)).all()
    
    # Filter uniques for debug loop too
    unique_curricula = []
    seen = set()
    for c in curricula:
        key = normalize_string(c.track or c.course_title)
        if key not in seen:
            unique_curricula.append(c)
            seen.add(key)

    header = f"{'Job Title':<30} | {'Cov':<6} | {'Rel':<6} | {'Mat':<3} | {'Gap':<3}"
    
    for i, c in enumerate(unique_curricula):
        if i >= 4: break 
        
        c_name = c.track or c.course_title or f"Curriculum {c.curriculum_id}"
        print(f"--- {c_name} ---")
        print(header)
        print("-" * 80)
        
        for j in jobs:
            # Skip blacklisted jobs in debug too (optional, keeps log clean)
            if (j.query or j.title or "").lower().strip() in BLACKLIST_JOBS:
                continue

            j_name = j.query or j.title or f"Job {j.job_id}"
            try:
                res = _calculate_gap_analysis(c.curriculum_id, j.job_id, db)
                print(f"{j_name:<30} | {res['coverage']:<6} | {res['relevance']:<6} | {res['matchingSkills']:<3} | {res['missingSkills']:<3}")
            except Exception as e:
                # pass silently
                pass
        print("\n")

    return []


# -----------------------
# CRUD Operations
# -----------------------
@router.post("/gapanalysis", response_model=GapAnalysisOut)
def create_report(data: GapAnalysisCreate, db: Session = Depends(get_db)):
    new_report = GapReport(**data.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/gapanalysis", response_model=List[GapAnalysisOut])
def get_reports(db: Session = Depends(get_db)):
    return db.query(GapReport).all()

@router.get("/gapanalysis/{report_id}", response_model=GapAnalysisOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    return report

@router.put("/gapanalysis/{report_id}", response_model=GapAnalysisOut)
def update_report(report_id: int, data: GapAnalysisBase, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    for key, value in data.dict().items(): setattr(report, key, value)
    db.commit()
    return report

@router.delete("/gapanalysis/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    db.delete(report)
    db.commit()
    return {"message": "Deleted"}

class RecommendationRequest(BaseModel):
    job_title: str
    curriculum_title: str
    missing_skills: List[str]
    coverage_score: float

@router.post("/api/recommend")
def generate_recommendation(request: RecommendationRequest):
    # Lazy import to avoid slowing down startup
    import google.generativeai as genai
    
    # Check if API key is present
    if not os.getenv("GOOGLE_API_KEY"):
        return {"recommendation": "⚠️ API Key missing. Please set GOOGLE_API_KEY in your backend environment."}
    
    # Configure Gemini on first use (lazy initialization)
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Limit skills to avoid token overflow
    skills_list = ", ".join(request.missing_skills[:15])
    
    # --- CONCISE PROMPT FOR STUDENTS & PROFESSORS ---
    prompt = f"""
    You are a curriculum advisor for CICS analyzing gap between "{request.curriculum_title}" and "{request.job_title}" roles.

    Match Score: {request.coverage_score}%
    Top Missing Skills: {skills_list}

    Provide a scan-friendly response with this EXACT structure:

    **Gap Summary:**
    (3-4 sentences) - Analyze the alignment issue:
    - What categories of skills are missing? (e.g., cloud platforms, statistical methods, tools)
    - Why does this gap matter for graduates entering this role?
    - What's the strategic impact on curriculum competitiveness?
    
    **Top 3 Actions:**
    List ONLY 3 specific syllabus updates:
    - Start each with a verb (Add, Integrate, Update, Include)
    - Keep each to 1 line
    - Focus on course content/labs only (NO internships, seminars, or general education)
    - Be specific to technical topics

    Use bullet points. Bold key terms only. Do NOT add a title or heading before "Gap Summary".
    """
    # -------------------------------------------------------
    
    # Recommended models by Gemini (in priority order)
    FALLBACK_MODELS = [
        'gemini-2.5-flash-lite',  # Fastest, separate quota pool
        'gemini-2.5-flash',       # Balanced performance
        'gemini-2.5-pro',         # Most capable
    ]
    
    # Try each model in sequence until one succeeds
    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            if hasattr(genai, "GenerativeModel"):
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = getattr(response, "text", None) or str(response)
                return {"recommendation": text}
            else:
                # Legacy fallback (for older SDK versions)
                response = genai.generate_text(
                    model="models/text-bison-001",
                    prompt=prompt
                )
                text = getattr(response, "result", None)
                if not text and isinstance(response, dict):
                    text = response.get("generated_text") or response.get("result")
                if not text:
                    text = str(response)
                return {"recommendation": text}
                
        except Exception as e:
            error_msg = str(e).lower()
            last_error = e
            
            # If it's a quota/rate limit error, try next model
            if any(keyword in error_msg for keyword in ['quota', 'limit', 'rate', 'resource_exhausted']):
                print(f"⚠️ {model_name} quota exceeded, trying next model...")
                continue
            else:
                # If it's a different error, fail immediately
                print(f"❌ Gemini API Error ({model_name}): {e}")
                break
    
    # All models failed
    print(f"❌ All models failed. Last error: {last_error}")
    return {"recommendation": "Unable to generate AI recommendations at this time. Please try again later."}
