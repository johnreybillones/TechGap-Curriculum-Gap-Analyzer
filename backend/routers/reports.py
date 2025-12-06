from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

# Import modules from your existing backend structure
# Assuming get_db is a standard function in database.py
from app.database import SessionLocal 
from app.models import Curriculum, Skill, JobRole, JobSkill 


# --- Pydantic Schemas for API Response ---
class Metric(BaseModel):
    """Schema for a named count/sum metric."""
    name: str = Field(..., example="Python")
    count: int = Field(..., example=150)

    class Config:
        from_attributes = True

class DashboardReport(BaseModel):
    """The main dashboard report structure."""
    total_courses: int = Field(..., description="Total number of courses.")
    total_skills: int = Field(..., description="Total number of unique skills.")
    total_jobs: int = Field(..., description="Total number of job postings.")
    total_gaps: int = Field(..., description="Total number of recorded skill gaps.")
    top_needed_skills: List[Metric] = Field(..., description="Top 5 most demanded skills based on summed importance.")


# --- Database Dependency (simplified for router context) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- FastAPI Router Definition ---
router = APIRouter()

@router.get(
    "/dashboard",
    response_model=DashboardReport,
    summary="Get aggregated data for the main dashboard report."
)
def get_dashboard_report(db: Session = Depends(get_db)):
    # 1. Basic Counts
    total_courses = db.query(Course).count()
    total_skills = db.query(Skill).count()
    total_jobs = db.query(JobPosting).count()
    total_gaps = db.query(GapAnalysis).count()

    # 2. Top 5 Most Needed Skills (Aggregation Query)
    # This query sums the 'importance_level' from the JobSkill table for each skill
    # and orders them to find the top 5 most demanded skills.
    top_skills_query = (
        db.query(
            Skill.skill_name,
            func.sum(JobSkill.importance_level).label("total_importance")
        )
        .join(JobSkill, Skill.skill_id == JobSkill.skill_id)
        .group_by(Skill.skill_id, Skill.skill_name)
        .order_by(desc("total_importance"))
        .limit(5)
        .all()
    )

    # Map the query results to the Pydantic Metric model
    top_skills_metrics: List[Metric] = [
        Metric(name=skill_name, count=int(total_importance))
        for skill_name, total_importance in top_skills_query
    ]

    # 3. Return the aggregated report
    return DashboardReport(
        total_courses=total_courses,
        total_skills=total_skills,
        total_jobs=total_jobs,
        total_gaps=total_gaps,
        top_needed_skills=top_skills_metrics,
    )