from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import GapReport, Curriculum, Skill
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/gap-report", tags=["Gap Report"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ SCHEMAS ------------------
class GapReportBase(BaseModel):
    curriculum_id: int
    missing_skill_id: Optional[int] = None
    recommendation: Optional[str] = None
    generated_by: Optional[str] = None
    date_generated: Optional[datetime] = None


class GapReportCreate(GapReportBase):
    pass


class GapReportOut(GapReportBase):
    report_id: int

    class Config:
        from_attributes = True


# ------------------ ROUTES ------------------
@router.post("/", response_model=GapReportOut)
def create_gap_report(data: GapReportCreate, db: Session = Depends(get_db)):
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == data.curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    if data.missing_skill_id is not None:
        skill = db.query(Skill).filter(Skill.skill_id == data.missing_skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")

    new_report = GapReport(**data.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/", response_model=List[GapReportOut])
def get_all_gap_reports(db: Session = Depends(get_db)):
    return db.query(GapReport).all()


@router.get("/{report_id}", response_model=GapReportOut)
def get_gap_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Gap Report not found")
    return report


@router.put("/{report_id}", response_model=GapReportOut)
def update_gap_report(
    report_id: int, data: GapReportBase, db: Session = Depends(get_db)
):
    gap_report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not gap_report:
        raise HTTPException(status_code=404, detail="Gap Report not found")

    # If missing_skill_id is being updated, validate it
    if data.missing_skill_id is not None:
        skill = db.query(Skill).filter(Skill.skill_id == data.missing_skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")

    for key, value in data.dict().items():
        setattr(gap_report, key, value)

    db.commit()
    db.refresh(gap_report)
    return gap_report


@router.delete("/{report_id}")
def delete_gap_report(report_id: int, db: Session = Depends(get_db)):
    gap_report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not gap_report:
        raise HTTPException(status_code=404, detail="Gap Report not found")

    db.delete(gap_report)
    db.commit()
    return {"message": "Gap Report deleted successfully"}
