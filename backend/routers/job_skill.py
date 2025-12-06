from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import JobSkill, JobRole, Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/job-skill", tags=["Job Skill"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ SCHEMAS ------------------
class JobSkillBase(BaseModel):
    job_id: int
    skill_id: int

class JobSkillCreate(JobSkillBase):
    pass

class JobSkillOut(JobSkillBase):
    class Config:
        from_attributes = True  # Pydantic v2 (previously orm_mode)

# ------------------ ROUTES ------------------

@router.post("/", response_model=JobSkillOut)
def create_job_skill(data: JobSkillCreate, db: Session = Depends(get_db)):
    job_role = db.query(JobRole).filter(JobRole.job_id == data.job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="JobRole not found")
    
    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Prevent duplicates (optional but nicer than letting PK error bubble up)
    existing = db.query(JobSkill).filter(
        JobSkill.job_id == data.job_id,
        JobSkill.skill_id == data.skill_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="JobSkill already exists")

    new_job_skill = JobSkill(
        job_id=data.job_id,
        skill_id=data.skill_id,
    )
    db.add(new_job_skill)
    db.commit()
    db.refresh(new_job_skill)
    return new_job_skill

@router.get("/", response_model=List[JobSkillOut])
def get_all_job_skills(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
):
    return db.query(JobSkill).offset(offset).limit(limit).all()

@router.get("/{job_id}/{skill_id}", response_model=JobSkillOut)
def get_job_skill(job_id: int, skill_id: int, db: Session = Depends(get_db)):
    js = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id
    ).first()
    if not js:
        raise HTTPException(status_code=404, detail="JobSkill not found")
    return js

@router.delete("/{job_id}/{skill_id}")
def delete_job_skill(job_id: int, skill_id: int, db: Session = Depends(get_db)):
    js = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id
    ).first()
    if not js:
        raise HTTPException(status_code=404, detail="JobSkill not found")
    db.delete(js)
    db.commit()
    return {"message": "Job Skill deleted successfully"}
