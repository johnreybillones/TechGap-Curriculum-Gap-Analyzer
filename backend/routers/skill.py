from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/skills", tags=["Skills"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ SCHEMAS ------------------
class SkillBase(BaseModel):
    skill_name: str

class SkillCreate(SkillBase):
    pass

class SkillOut(SkillBase):
    skill_id: int

    class Config:
        from_attributes = True  # or orm_mode = True (Pydantic v1)


# ------------------ ROUTES ------------------

@router.post("/", response_model=SkillOut)
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    # Check if skill already exists
    existing_skill = db.query(Skill).filter(Skill.skill_name == data.skill_name).first()
    if existing_skill:
        raise HTTPException(status_code=400, detail="Skill already exists")

    new_skill = Skill(skill_name=data.skill_name)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.get("/", response_model=List[SkillOut])
def get_all_skills(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
):
    return db.query(Skill).offset(offset).limit(limit).all()


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=SkillOut)
def update_skill(skill_id: int, data: SkillBase, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Optional: prevent renaming to an existing skill_name
    if (
        data.skill_name != skill.skill_name
        and db.query(Skill)
            .filter(Skill.skill_name == data.skill_name)
            .first()
    ):
        raise HTTPException(status_code=400, detail="Skill name already in use")

    skill.skill_name = data.skill_name
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted successfully"}
