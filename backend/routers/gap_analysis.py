from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Curriculum,
    GapReport,
    JobRole,
    JobSkill,
    MatchResult,
    Skill,
    SkillMatchDetail,
)

router = APIRouter(tags=["Gap Analysis"])


# -----------------------
# Gap report CRUD
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


# -----------------------
# Analysis endpoint
# -----------------------
class AnalysisRequest(BaseModel):
    curriculum_id: int
    job_id: int


@router.post("/api/analyze")
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Compute coverage/alignment and skill gaps for a curriculum/job pair.
    """
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == request.curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    job = db.query(JobRole).filter(JobRole.job_id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job role not found")

    job_skill_ids = [
        row.skill_id
        for row in db.query(JobSkill).filter(JobSkill.job_id == request.job_id).all()
    ]

    details = (
        db.query(SkillMatchDetail)
        .filter(
            SkillMatchDetail.curriculum_id == request.curriculum_id,
            SkillMatchDetail.job_id == request.job_id,
        )
        .all()
    )

    if details:
        covered_ids = [
            d.skill_id for d in details if d.status in ("match", "partial")
        ]
        gap_ids = [d.skill_id for d in details if d.status == "gap"]
        similarity_scores = [d.similarity_score for d in details]
    else:
        covered_ids = []
        gap_ids = []
        similarity_scores = []

    # If we have job skills but no explicit gap_ids, treat the remainder as gaps
    if job_skill_ids and not gap_ids and not details:
        gap_ids = job_skill_ids

    matching_skills = len(covered_ids)
    missing_skills = len(gap_ids) if gap_ids else max(len(job_skill_ids) - matching_skills, 0)

    total_target_skills = len(job_skill_ids) if job_skill_ids else matching_skills + missing_skills
    coverage_ratio = (
        matching_skills / total_target_skills if total_target_skills > 0 else 0.0
    )

    avg_similarity = (
        sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    )

    def skill_names(ids: List[int]) -> List[str]:
        if not ids:
            return []
        rows = db.query(Skill.skill_name).filter(Skill.skill_id.in_(ids)).all()
        return [r[0] for r in rows]

    covered_names = skill_names(covered_ids)
    gap_names = skill_names(gap_ids)

    # Optional: include model score if present
    match_row = (
        db.query(MatchResult)
        .filter(
            MatchResult.curriculum_id == request.curriculum_id,
            MatchResult.job_id == request.job_id,
        )
        .order_by(MatchResult.computed_at.desc())
        .first()
    )
    alignment_score = avg_similarity if avg_similarity else (match_row.score if match_row else 0.0)

    return {
        "coverage": f"{coverage_ratio * 100:.1f}%",
        "alignment": f"{alignment_score * 100:.1f}%",
        "matchingSkills": matching_skills,
        "missingSkills": missing_skills,
        "covered": covered_names,
        "gaps": gap_names,
    }
@router.post("/gapanalysis", response_model=GapAnalysisOut)
def create_report(data: GapAnalysisCreate, db: Session = Depends(get_db)):
    course = (
        db.query(Curriculum).filter(Curriculum.curriculum_id == data.course_id).first()
    )
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
