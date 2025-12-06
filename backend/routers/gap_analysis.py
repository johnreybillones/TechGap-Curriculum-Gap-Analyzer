from datetime import date
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database import SessionLocal
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
# These jobs will NEVER appear in the dropdown, even if they exist in the DB.
BLACKLIST_JOBS = {
    "statistics",
    "business analyst",
    "data quality manager",
    "data warehousing",
    "technical operations"
}

# -----------------------
# Helpers
# -----------------------
def invalidate_options_cache():
    global _OPTIONS_CACHE
    _OPTIONS_CACHE = None

def normalize_string(text: str) -> str:
    """Aggressive normalization for deduplication."""
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
# ... existing imports ...

# Find the function _calculate_gap_analysis and replace it with this:

# ... (Imports remain the same)

# ... (Keep existing setup code until _calculate_gap_analysis)

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
            # STRICT LOGIC: If it's not a match, it's a gap.
            # We ignore 'partial' status as requested.
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
    
    # Fallback for division by zero
    if total_curriculum_skills == 0:
        total_curriculum_skills = match_count if match_count > 0 else 1

    coverage = (match_count / total_job_needs) if total_job_needs > 0 else 0.0
    relevance = (match_count / total_curriculum_skills) if total_curriculum_skills > 0 else 0.0
    if relevance > 1.0: relevance = 1.0
    
    return {
        "coverage": f"{coverage * 100:.1f}%",
        "relevance": f"{relevance * 100:.1f}%",
        "coverage_score": coverage * 100,   # Raw number for frontend charts
        "relevance_score": relevance * 100, # Raw number for frontend charts
        
        # Breakdown counts
        "matchingSkills": match_count,
        "missingSkills": gap_count,
        
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
# Filtered Options Endpoint (Deduplicated + Blacklist)
# -----------------------
@router.get("/api/options")
def get_options(db: Session = Depends(get_db)):
    """
    Returns Curricula and Jobs that exist in SkillMatchDetail.
    DEDUPLICATES options by name.
    REMOVES blacklisted jobs.
    """
    global _OPTIONS_CACHE
    if _OPTIONS_CACHE is not None:
        return _OPTIONS_CACHE

    # 1. Get IDs that actually have data
    valid_curriculum_ids = db.query(SkillMatchDetail.curriculum_id).distinct().all()
    valid_job_ids = db.query(SkillMatchDetail.job_id).distinct().all()
    
    c_ids = [row[0] for row in valid_curriculum_ids]
    j_ids = [row[0] for row in valid_job_ids]

    # 2. Fetch Entities
    curricula = db.query(Curriculum).filter(Curriculum.curriculum_id.in_(c_ids)).all()
    jobs = db.query(JobRole).filter(JobRole.job_id.in_(j_ids)).all()

    # 3. Format & Deduplicate Curricula
    curriculum_options = []
    seen_c = set()
    for c in curricula:
        label = c.track or c.course_title or ""
        norm = normalize_string(label)
        
        if norm and norm not in seen_c:
            curriculum_options.append({"id": c.curriculum_id, "label": label})
            seen_c.add(norm)
    
    # 4. Format & Deduplicate Jobs (WITH BLACKLIST CHECK)
    job_options = []
    seen_j = set()
    for j in jobs:
        label = j.query or j.title or ""
        
        # --- BLACKLIST CHECK ---
        # Check if the exact label (lowercase) is in our banned list
        if label.lower().strip() in BLACKLIST_JOBS:
            continue
            
        norm = normalize_string(label)
        
        if norm and norm not in seen_j:
            job_options.append({"id": j.job_id, "label": label})
            seen_j.add(norm)

    _OPTIONS_CACHE = {"curricula": curriculum_options, "jobs": job_options}
    return _OPTIONS_CACHE


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