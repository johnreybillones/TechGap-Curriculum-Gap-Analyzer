from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import SkillMatchDetail, Curriculum, JobRole, Skill
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime

router = APIRouter(prefix="/skill-match-detail", tags=["Skill Match Detail"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


StatusType = Literal["match", "partial", "gap"]


# ------------------ SCHEMAS ------------------
class SkillMatchDetailBase(BaseModel):
    curriculum_id: int
    job_id: int
    skill_id: int
    similarity_score: float
    status: StatusType
    model: str


class SkillMatchDetailCreate(SkillMatchDetailBase):
    pass


class SkillMatchDetailOut(SkillMatchDetailBase):
    detail_id: int
    computed_at: datetime

    class Config:
        from_attributes = True


# ------------------ ROUTES ------------------
@router.post("/", response_model=SkillMatchDetailOut)
def create_skill_match_detail(
    data: SkillMatchDetailCreate, db: Session = Depends(get_db)
):
    # Validate foreign keys
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == data.curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    job = db.query(JobRole).filter(JobRole.job_id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Role not found")

    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    new_detail = SkillMatchDetail(**data.dict())
    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail


@router.get("/", response_model=List[SkillMatchDetailOut])
def get_all_skill_match_details(db: Session = Depends(get_db)):
    return db.query(SkillMatchDetail).all()


@router.get("/{detail_id}", response_model=SkillMatchDetailOut)
def get_skill_match_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = (
        db.query(SkillMatchDetail)
        .filter(SkillMatchDetail.detail_id == detail_id)
        .first()
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Skill Match Detail not found")
    return detail


@router.get(
    "/by-course-job/{curriculum_id}/{job_id}",
    response_model=List[SkillMatchDetailOut],
)
def get_by_curriculum_and_job(
    curriculum_id: int, job_id: int, db: Session = Depends(get_db)
):
    details = (
        db.query(SkillMatchDetail)
        .filter(
            SkillMatchDetail.curriculum_id == curriculum_id,
            SkillMatchDetail.job_id == job_id,
        )
        .all()
    )
    return details


class SkillMatchDetailUpdate(BaseModel):
    similarity_score: float
    status: StatusType
    model: str


@router.put("/{detail_id}", response_model=SkillMatchDetailOut)
def update_skill_match_detail(
    detail_id: int, data: SkillMatchDetailUpdate, db: Session = Depends(get_db)
):
    detail = (
        db.query(SkillMatchDetail)
        .filter(SkillMatchDetail.detail_id == detail_id)
        .first()
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Skill Match Detail not found")

    for key, value in data.dict().items():
        setattr(detail, key, value)

    db.commit()
    db.refresh(detail)
    return detail


@router.delete("/{detail_id}")
def delete_skill_match_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = (
        db.query(SkillMatchDetail)
        .filter(SkillMatchDetail.detail_id == detail_id)
        .first()
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Skill Match Detail not found")

    db.delete(detail)
    db.commit()
    return {"message": "Skill Match Detail deleted successfully"}
