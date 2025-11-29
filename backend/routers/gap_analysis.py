from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import GapAnalysis, Course, Skill
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/gapanalysis", tags=["Gap Analysis"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
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
        orm_mode = True

# Routes
@router.post("/", response_model=GapAnalysisOut)
def create_report(data: GapAnalysisCreate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    skill = db.query(Skill).filter(Skill.skill_id == data.missing_skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    new_report = GapAnalysis(**data.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/", response_model=List[GapAnalysisOut])
def get_reports(db: Session = Depends(get_db)):
    return db.query(GapAnalysis).all()

@router.get("/{report_id}", response_model=GapAnalysisOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapAnalysis).filter(GapAnalysis.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    return report

@router.put("/{report_id}", response_model=GapAnalysisOut)
def update_report(report_id: int, data: GapAnalysisBase, db: Session = Depends(get_db)):
    report = db.query(GapAnalysis).filter(GapAnalysis.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    for key, value in data.dict().items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return report

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapAnalysis).filter(GapAnalysis.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="GapAnalysis not found")
    db.delete(report)
    db.commit()
    return {"message": "GapAnalysis report deleted successfully"}
