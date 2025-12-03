from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import JobRole
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/job-role", tags=["Job Role"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ SCHEMAS ------------------
class JobRoleBase(BaseModel):
    title: str
    query: Optional[str] = None      # ⬅ NEW
    profile_text: Optional[str] = None


class JobRoleCreate(JobRoleBase):
    pass


class JobRoleOut(JobRoleBase):
    job_id: int

    class Config:
        from_attributes = True



# ------------------ ROUTES ------------------
@router.post("/", response_model=JobRoleOut)
def create_job_role(data: JobRoleCreate, db: Session = Depends(get_db)):
    new_job_role = JobRole(**data.dict())
    db.add(new_job_role)
    db.commit()
    db.refresh(new_job_role)
    return new_job_role


@router.get("/", response_model=List[JobRoleOut])
def get_job_roles(db: Session = Depends(get_db)):
    return db.query(JobRole).all()


@router.get("/{job_id}", response_model=JobRoleOut)
def get_job_role(job_id: int, db: Session = Depends(get_db)):
    job_role = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job Role not found")
    return job_role


@router.put("/{job_id}", response_model=JobRoleOut)
def update_job_role(job_id: int, data: JobRoleBase, db: Session = Depends(get_db)):
    job_role = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job Role not found")

    for key, value in data.dict().items():
        setattr(job_role, key, value)

    db.commit()
    db.refresh(job_role)
    return job_role


@router.delete("/{job_id}")
def delete_job_role(job_id: int, db: Session = Depends(get_db)):
    job_role = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job Role not found")

    db.delete(job_role)
    db.commit()
    return {"message": "Job Role deleted successfully"}
