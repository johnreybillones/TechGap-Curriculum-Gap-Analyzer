from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import JobSkill, JobPosting, Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/jobskills", tags=["Job Skills"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class JobSkillBase(BaseModel):
    job_id: int
    skill_id: int
    importance_level: int

class JobSkillCreate(JobSkillBase):
    pass

class JobSkillOut(JobSkillBase):
    class Config:
        orm_mode = True

# Routes
@router.post("/", response_model=JobSkillOut)
def create_jobskill(data: JobSkillCreate, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.job_id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = db.query(JobSkill).filter(
        JobSkill.job_id == data.job_id,
        JobSkill.skill_id == data.skill_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="JobSkill already exists")

    new_js = JobSkill(**data.dict())
    db.add(new_js)
    db.commit()
    db.refresh(new_js)
    return new_js

@router.get("/", response_model=List[JobSkillOut])
def get_all_jobskills(db: Session = Depends(get_db)):
    return db.query(JobSkill).all()

@router.get("/{job_id}/{skill_id}", response_model=JobSkillOut)
def get_jobskill(job_id: int, skill_id: int, db: Session = Depends(get_db)):
    js = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id
    ).first()
    if not js:
        raise HTTPException(status_code=404, detail="JobSkill not found")
    return js

@router.put("/{job_id}/{skill_id}", response_model=JobSkillOut)
def update_jobskill(job_id: int, skill_id: int, data: JobSkillBase, db: Session = Depends(get_db)):
    js = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id
    ).first()
    if not js:
        raise HTTPException(status_code=404, detail="JobSkill not found")
    js.importance_level = data.importance_level
    db.commit()
    db.refresh(js)
    return js

@router.delete("/{job_id}/{skill_id}")
def delete_jobskill(job_id: int, skill_id: int, db: Session = Depends(get_db)):
    js = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id
    ).first()
    if not js:
        raise HTTPException(status_code=404, detail="JobSkill not found")
    db.delete(js)
    db.commit()
    return {"message": "JobSkill deleted successfully"}
