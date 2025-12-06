from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import CourseSkill, Curriculum, Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/courseskills", tags=["Course Skills"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ SCHEMAS ------------------
class CourseSkillBase(BaseModel):
    course_id: int
    skill_id: int
    relevance_level: int

class CourseSkillCreate(CourseSkillBase):
    pass

class CourseSkillUpdate(BaseModel):
    relevance_level: int  

class CourseSkillOut(CourseSkillBase):
    class Config:
        from_attributes = True

# ------------------ ROUTES ------------------

@router.post("/", response_model=CourseSkillOut)
def create_course_skill(data: CourseSkillCreate, db: Session = Depends(get_db)):
    # checks if course_id exists in courses
    course = db.query(Curriculum).filter(Curriculum.curriculum_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # check if the skill_id exists in skills
    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # check duplicates
    existing = db.query(CourseSkill).filter(
        CourseSkill.course_id == data.course_id,
        CourseSkill.skill_id == data.skill_id
    ).first()

    # prevents duplicates
    if existing:
        raise HTTPException(status_code=400, detail="CourseSkill already exists")

    new_cs = CourseSkill(
        course_id=data.course_id,
        skill_id=data.skill_id,
        relevance_level=data.relevance_level
    )
    db.add(new_cs)
    db.commit()
    db.refresh(new_cs)
    return new_cs

# fetch all the rows from courseskills
@router.get("/", response_model=List[CourseSkillOut])
def get_all_course_skills(db: Session = Depends(get_db)):
    return db.query(CourseSkill).all()

@router.get("/{course_id}/{skill_id}", response_model=CourseSkillOut)
def get_course_skill(course_id: int, skill_id: int, db: Session = Depends(get_db)):
    # searches the courseskills table for a record that matches both ids
    cs = db.query(CourseSkill).filter(
        CourseSkill.course_id == course_id,
        CourseSkill.skill_id == skill_id
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="CourseSkill not found")
    return cs

@router.put("/{course_id}/{skill_id}", response_model=CourseSkillOut)
# updates the relevance level of an existing course-skill link
def update_course_skill(course_id: int, skill_id: int, data: CourseSkillUpdate, db: Session = Depends(get_db)):
    cs = db.query(CourseSkill).filter(
        CourseSkill.course_id == course_id,
        CourseSkill.skill_id == skill_id
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="CourseSkill not found")

    cs.relevance_level = data.relevance_level
    db.commit()
    db.refresh(cs)
    return cs

@router.delete("/{course_id}/{skill_id}")
# deletes a specific course-skill link
def delete_course_skill(course_id: int, skill_id: int, db: Session = Depends(get_db)):
    cs = db.query(CourseSkill).filter(
        CourseSkill.course_id == course_id,
        CourseSkill.skill_id == skill_id
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="CourseSkill not found")

    db.delete(cs)
    db.commit()
    return {"message": "CourseSkill deleted successfully"}
