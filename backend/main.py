from fastapi import FastAPI
from routers import courses, skills, job_postings, course_skills, job_skills, gap_analysis, reports

app = FastAPI(title="TechGap API")

# Register routers (all must have: router = APIRouter() inside their files)
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(skills.router, prefix="/skills", tags=["Skills"])
app.include_router(job_postings.router, prefix="/jobs", tags=["Job Postings"])
app.include_router(course_skills.router, prefix="/course-skills", tags=["Course Skills"])
app.include_router(job_skills.router, prefix="/job-skills", tags=["Job Skills"])
app.include_router(gap_analysis.router, prefix="/gap", tags=["Gap Analysis"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

@app.get("/")
def root():
    return {"message": "Curriculum Gap Analyzer API is running 🚀"}