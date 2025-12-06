from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Curriculum
from pydantic import BaseModel
from typing import List, Optional, Literal

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Allowed track values (must match MySQL ENUM + models.py)
TrackType = Literal[
    "CS Intelligent Systems",
    "CS Game Development",
    "IT Web Development",
    "IT Network Technology",
    "Other",
]


# ------------------ SCHEMAS ------------------
class CurriculumBase(BaseModel):
    track: TrackType
    course_title: str
    course_code: Optional[str] = None
    raw_description: Optional[str] = None


class CurriculumCreate(CurriculumBase):
    pass


class CurriculumOut(CurriculumBase):
    curriculum_id: int

    class Config:
        from_attributes = True


# ------------------ ROUTES ------------------
@router.post("/", response_model=CurriculumOut)
def create_curriculum(data: CurriculumCreate, db: Session = Depends(get_db)):
    new_curriculum = Curriculum(**data.dict())
    db.add(new_curriculum)
    db.commit()
    db.refresh(new_curriculum)
    return new_curriculum


@router.get("/", response_model=List[CurriculumOut])
def get_curricula(db: Session = Depends(get_db)):
    return db.query(Curriculum).all()


@router.get("/{curriculum_id}", response_model=CurriculumOut)
def get_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum


@router.put("/{curriculum_id}", response_model=CurriculumOut)
def update_curriculum(
    curriculum_id: int, data: CurriculumBase, db: Session = Depends(get_db)
):
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    for key, value in data.dict().items():
        setattr(curriculum, key, value)

    db.commit()
    db.refresh(curriculum)
    return curriculum


@router.delete("/{curriculum_id}")
def delete_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    curriculum = (
        db.query(Curriculum)
        .filter(Curriculum.curriculum_id == curriculum_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    db.delete(curriculum)
    db.commit()
    return {"message": "Curriculum deleted successfully"}
