from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Course
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/courses", tags=["Courses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class CourseBase(BaseModel):
    course_code: str
    course_name: str
    description: Optional[str] = None
    department: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    course_id: int
    class Config:
        orm_mode = True

# Routes
@router.post("/", response_model=CourseOut)
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(**data.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[CourseOut])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, data: CourseBase, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in data.dict().items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
