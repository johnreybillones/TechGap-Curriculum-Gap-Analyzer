from datetime import date
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import csv
from pathlib import Path
from sqlalchemy import func
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
# Analysis Endpoint
# -----------------------
@router.post("/api/analyze")
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyzes the gap between a Curriculum and a specific Job Role.
    
    LOGIC VERIFICATION:
    1. Matching Skills:
       - Source: Union of DB (SkillMatchDetail) and CSV.
       - Filter: Strictly filtered by the specific job_id / job_title.
       - Result: Only skills found in BOTH the Curriculum and THIS Job.
       
    2. Missing Skills:
       - Source: Union of DB (GapReport) and CSV.
       - Filter: Intersected with 'Target Job Skills' (from JobSkill table).
       - Result: Only skills found in THIS Job but MISSING from Curriculum.
       
    3. Metrics:
       - Coverage: Matches / (Matches + Relevant Gaps) -> Specific to Job.
       - Relevance: Matches / Total Curriculum -> Specific to Course Efficiency.
    """
    # 1. Fetch Entities
    curriculum = db.query(Curriculum).filter(Curriculum.curriculum_id == request.curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    job = db.query(JobRole).filter(JobRole.job_id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job role not found")

    # Helper for normalization
    def normalize_skill(name):
        if not name: return ""
        return re.sub(r'[^a-z0-9]', '', name.lower())

    # 2. Get Target Job Skills (The "Requirement List" for THIS Job)
    # Priority A: From Database
    job_skill_rows = (
        db.query(Skill.skill_name)
        .join(JobSkill, Skill.skill_id == JobSkill.skill_id)
        .filter(JobSkill.job_id == request.job_id)
        .all()
    )
    target_job_skills_norm = {normalize_skill(r.skill_name) for r in job_skill_rows}

    # Priority B: From CSV (If DB is empty)
    csv_path_detail = Path(__file__).resolve().parent.parent / "csvs" / "generated csv from model and ung model file" / "skill_match_detail.csv"
    
    if not target_job_skills_norm and csv_path_detail.exists():
        job_label = (job.query or job.title or "").lower()
        
        with csv_path_detail.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                jt = row.get("job_title", "").lower()
                # Loose match for job title
                if job_label and (job_label in jt or jt in job_label):
                    # Add ALL skills associated with this job (Matches AND Gaps)
                    s_name = row.get("skill_name", "").strip()
                    if s_name:
                        target_job_skills_norm.add(normalize_skill(s_name))

    # 3. Get Curriculum Skills (DB Inventory)
    curriculum_skill_rows = (
        db.query(Skill.skill_name)
        .join(CourseSkill, Skill.skill_id == CourseSkill.skill_id)
        .filter(CourseSkill.curriculum_id == request.curriculum_id)
        .all()
    )
    curriculum_skills_count = len(curriculum_skill_rows)

    # =========================================================
    # PART A: MATCHING SKILLS (Merge DB + CSV)
    # =========================================================
    covered_names = set()
    covered_names_norm = set() 
    similarity_scores = []
    
    # 1. From DB
    details = (
        db.query(SkillMatchDetail)
        .filter(
            SkillMatchDetail.curriculum_id == request.curriculum_id,
            SkillMatchDetail.job_id == request.job_id,
        )
        .all()
    )
    if details:
        for d in details:
            if d.status in ("match", "partial"):
                s = db.query(Skill).get(d.skill_id)
                if s:
                    s_name = s.skill_name
                    covered_names.add(s_name)
                    covered_names_norm.add(normalize_skill(s_name))
                    similarity_scores.append(d.similarity_score)

    # 2. From CSV (Merge if available)
    if csv_path_detail.exists():
        job_label = (job.query or job.title or "").lower()
        track_label = (curriculum.track or curriculum.course_title or "").lower()
        
        with csv_path_detail.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("curriculum_track", "").lower() != track_label: continue
                
                jt = row.get("job_title", "").lower()
                if job_label and (job_label in jt or jt in job_label):
                    if row.get("status", "").lower() in ("match", "partial"):
                        s_name = row.get("skill_name", "").strip()
                        if s_name:
                            # Avoid duplicates via normalized check
                            if normalize_skill(s_name) not in covered_names_norm:
                                covered_names.add(s_name)
                                covered_names_norm.add(normalize_skill(s_name))
                                try:
                                    similarity_scores.append(float(row.get("similarity_score", 0)))
                                except:
                                    pass

    # =========================================================
    # PART B: POTENTIAL GAPS (Merge DB + CSV)
    # =========================================================
    raw_gap_pool = set() # Stores actual names
    raw_gap_pool_norm = {} # Maps normalized -> original name

    # 1. From DB (GapReport)
    gap_reports = db.query(GapReport).filter(GapReport.curriculum_id == request.curriculum_id).all()
    for gr in gap_reports:
        if gr.recommendation:
            match = re.search(r":\s*(.*?)$", gr.recommendation)
            if match:
                s_name = match.group(1).strip()
                raw_gap_pool.add(s_name)
                raw_gap_pool_norm[normalize_skill(s_name)] = s_name

    # 2. From CSV (GapReport fallback)
    csv_path_gaps = Path(__file__).resolve().parent.parent / "csvs" / "generated csv from model and ung model file" / "gap_report.csv"
    if csv_path_gaps.exists():
        track_label = (curriculum.track or curriculum.course_title or "").lower()
        with csv_path_gaps.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("curriculum_track", "").lower() == track_label:
                    rec = row.get("recommendation", "")
                    match = re.search(r":\s*(.*?)$", rec)
                    if match:
                        s_name = match.group(1).strip()
                        if normalize_skill(s_name) not in raw_gap_pool_norm:
                            raw_gap_pool.add(s_name)
                            raw_gap_pool_norm[normalize_skill(s_name)] = s_name

    # =========================================================
    # PART C: STRICT JOB-SPECIFIC FILTERING
    # =========================================================
    
    # We strictly intersect the "Raw Gaps" (from Curriculum analysis) 
    # with "Target Job Skills" (from Job Requirements).
    # This guarantees we ONLY show gaps relevant to THIS job.
    
    final_gaps = set()
    
    if target_job_skills_norm:
        for gap_norm, gap_original in raw_gap_pool_norm.items():
            if gap_norm in target_job_skills_norm:
                final_gaps.add(gap_original)
    
    # Sanity check: Remove anything we already matched
    # (Matches take precedence over Gaps)
    final_gaps_cleaned = set()
    for gap in final_gaps:
        if normalize_skill(gap) not in covered_names_norm:
            final_gaps_cleaned.add(gap)

    matching_skills_count = len(covered_names)
    missing_skills_count = len(final_gaps_cleaned)
    
    # Denominators
    total_market_skills = matching_skills_count + missing_skills_count
    
    # If curriculum count is 0 (import error) but matches exist, infer curriculum size
    if curriculum_skills_count == 0 and matching_skills_count > 0:
        curriculum_skills_count = matching_skills_count

    # METRIC 1: Coverage (Matches / Job Requirements)
    coverage_ratio = (
        matching_skills_count / total_market_skills if total_market_skills > 0 else 0.0
    )

    # METRIC 2: Relevance (Matches / Curriculum Inventory)
    relevance_ratio = (
        matching_skills_count / curriculum_skills_count if curriculum_skills_count > 0 else 0.0
    )
    if relevance_ratio > 1.0: relevance_ratio = 1.0

    avg_similarity = (
        sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    )

    return {
        "coverage": f"{coverage_ratio * 100:.1f}%",
        "relevance": f"{relevance_ratio * 100:.1f}%",
        "alignment": f"{avg_similarity * 100:.1f}%",
        "matchingSkills": matching_skills_count,
        "missingSkills": missing_skills_count,
        "covered": sorted(list(covered_names)),
        "gaps": sorted(list(final_gaps_cleaned)),
    }


# -----------------------
# CRUD Operations
# -----------------------
@router.post("/gapanalysis", response_model=GapAnalysisOut)
def create_report(data: GapAnalysisCreate, db: Session = Depends(get_db)):
    course = db.query(Curriculum).filter(Curriculum.curriculum_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    skill = db.query(Skill).filter(Skill.skill_id == data.missing_skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

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
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    return report

@router.put("/gapanalysis/{report_id}", response_model=GapAnalysisOut)
def update_report(report_id: int, data: GapAnalysisBase, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    for key, value in data.dict().items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return report

@router.delete("/gapanalysis/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    db.delete(report)
    db.commit()
    return {"message": "GapAnalysis report deleted successfully"}

@router.get("/api/options")
def get_options(db: Session = Depends(get_db)):
    curr_counts = (
        db.query(SkillMatchDetail.curriculum_id.label("cid"), func.count().label("cnt"))
        .group_by(SkillMatchDetail.curriculum_id).all()
    )
    job_counts = (
        db.query(SkillMatchDetail.job_id.label("jid"), func.count().label("cnt"))
        .group_by(SkillMatchDetail.job_id).all()
    )

    def build_curr_options(ids_with_counts):
        opts = {}
        for cid, cnt in ids_with_counts:
            row = db.query(Curriculum).filter(Curriculum.curriculum_id == cid).first()
            if not row: continue
            label = row.track or row.course_title or f"Curriculum {cid}"
            if label not in opts or cnt > opts[label]["count"]:
                opts[label] = {"id": cid, "label": label, "count": cnt}
        return list(opts.values())

    def build_job_options(ids_with_counts):
        opts = {}
        for jid, cnt in ids_with_counts:
            row = db.query(JobRole).filter(JobRole.job_id == jid).first()
            if not row: continue
            label = row.query or row.title or f"Job {jid}"
            if label not in opts or cnt > opts[label]["count"]:
                opts[label] = {"id": jid, "label": label, "count": cnt}
        return list(opts.values())

    curriculum_options = build_curr_options(curr_counts)
    job_options = build_job_options(job_counts)

    if not curriculum_options:
        curriculum_options = [{"id": c.curriculum_id, "label": c.track or c.course_title} for c in db.query(Curriculum).all()]
    if not job_options:
        job_options = [{"id": j.job_id, "label": j.query or j.title} for j in db.query(JobRole).all()]

    return {"curricula": curriculum_options, "jobs": job_options}