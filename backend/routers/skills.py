from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Skill
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/skills", tags=["Skills"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class SkillBase(BaseModel):
    skill_name: str
    category: str

class SkillCreate(SkillBase):
    pass

class SkillOut(SkillBase):
    skill_id: int
    class Config:
        orm_mode = True

# Routes
@router.post("/", response_model=SkillOut)
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    skill = Skill(**data.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.get("/", response_model=List[SkillOut])
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()

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
    for key, value in data.dict().items():
        setattr(skill, key, value)
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
