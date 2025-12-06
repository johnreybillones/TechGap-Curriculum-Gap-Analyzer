from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import JobRole
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/jobpostings", tags=["Job Postings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class JobPostingBase(BaseModel):
    job_title: str
    company: Optional[str] = None
    description: str
    source: Optional[str] = None
    date_posted: Optional[date] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingOut(JobPostingBase):
    job_id: int
    class Config:
        from_attributes = True

# Routes
@router.post("/", response_model=JobPostingOut)
def create_jobposting(data: JobPostingCreate, db: Session = Depends(get_db)):
    job = JobRole(**data.dict())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/", response_model=List[JobPostingOut])
def get_jobpostings(db: Session = Depends(get_db)):
    return db.query(JobRole).all()

@router.get("/{job_id}", response_model=JobPostingOut)
def get_jobposting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobPostingOut)
def update_jobposting(job_id: int, data: JobPostingBase, db: Session = Depends(get_db)):
    job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in data.dict().items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}")
def delete_jobposting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
