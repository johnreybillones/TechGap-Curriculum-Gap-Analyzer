from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MatchResult, Curriculum, JobRole
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/match-result", tags=["Match Result"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ SCHEMAS ------------------
class MatchResultBase(BaseModel):
    curriculum_id: int
    job_id: int
    score: float
    rank_small: int
    model: str

class MatchResultOut(MatchResultBase):
    match_id: int

    class Config:
        from_attributes = True

# ------------------ ROUTES ------------------

@router.post("/", response_model=MatchResultOut)
def create_match_result(data: MatchResultBase, db: Session = Depends(get_db)):
    new_match_result = MatchResult(**data.dict())
    db.add(new_match_result)
    db.commit()
    db.refresh(new_match_result)
    return new_match_result

@router.get("/", response_model=List[MatchResultOut])
def get_all_match_results(db: Session = Depends(get_db)):
    return db.query(MatchResult).all()

@router.get("/{match_id}", response_model=MatchResultOut)
def get_match_result(match_id: int, db: Session = Depends(get_db)):
    match_result = db.query(MatchResult).filter(MatchResult.match_id == match_id).first()
    if not match_result:
        raise HTTPException(status_code=404, detail="Match Result not found")
    return match_result

@router.put("/{match_id}", response_model=MatchResultOut)
def update_match_result(match_id: int, data: MatchResultBase, db: Session = Depends(get_db)):
    match_result = db.query(MatchResult).filter(MatchResult.match_id == match_id).first()
    if not match_result:
        raise HTTPException(status_code=404, detail="Match Result not found")
    for key, value in data.dict().items():
        setattr(match_result, key, value)
    db.commit()
    db.refresh(match_result)
    return match_result

@router.delete("/{match_id}")
def delete_match_result(match_id: int, db: Session = Depends(get_db)):
    match_result = db.query(MatchResult).filter(MatchResult.match_id == match_id).first()
    if not match_result:
        raise HTTPException(status_code=404, detail="Match Result not found")
    db.delete(match_result)
    db.commit()
    return {"message": "Match Result deleted successfully"}