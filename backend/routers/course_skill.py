from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import CourseSkill, Curriculum, Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/course-skills", tags=["Course Skill"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ SCHEMAS ------------------
class CourseSkillBase(BaseModel):
    curriculum_id: int
    skill_id: int

class CourseSkillCreate(CourseSkillBase):
    pass

class CourseSkillOut(CourseSkillBase):
    class Config:
        from_attributes = True  # or orm_mode = True if you're on Pydantic v1

# ------------------ ROUTES ------------------

@router.post("/", response_model=CourseSkillOut)
def create_course_skill(data: CourseSkillCreate, db: Session = Depends(get_db)):
    # Check if curriculum exists
    curriculum = db.query(Curriculum).filter(
        Curriculum.curriculum_id == data.curriculum_id
    ).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    # Check if skill exists
    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Prevent duplicates
    existing = db.query(CourseSkill).filter(
        CourseSkill.curriculum_id == data.curriculum_id,
        CourseSkill.skill_id == data.skill_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="CourseSkill already exists")

    new_course_skill = CourseSkill(
        curriculum_id=data.curriculum_id,
        skill_id=data.skill_id,
    )
    db.add(new_course_skill)
    db.commit()
    db.refresh(new_course_skill)
    return new_course_skill


@router.get("/", response_model=List[CourseSkillOut])
def get_all_course_skills(db: Session = Depends(get_db)):
    return db.query(CourseSkill).all()


@router.get("/{curriculum_id}/{skill_id}", response_model=CourseSkillOut)
def get_course_skill(curriculum_id: int, skill_id: int, db: Session = Depends(get_db)):
    cs = db.query(CourseSkill).filter(
        CourseSkill.curriculum_id == curriculum_id,
        CourseSkill.skill_id == skill_id,
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="CourseSkill not found")
    return cs


@router.delete("/{curriculum_id}/{skill_id}")
def delete_course_skill(curriculum_id: int, skill_id: int, db: Session = Depends(get_db)):
    cs = db.query(CourseSkill).filter(
        CourseSkill.curriculum_id == curriculum_id,
        CourseSkill.skill_id == skill_id,
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="CourseSkill not found")

    db.delete(cs)
    db.commit()
    return {"message": "CourseSkill deleted successfully"}
