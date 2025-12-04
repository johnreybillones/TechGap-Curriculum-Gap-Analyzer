from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    curriculum,
    job_role,
    course_skill,
    job_skill,
    embedding,
    gap_report,
    skill,
    match_result,
    skill_match_detail,
    gap_analysis,
)
from routers import routers as predict

app = FastAPI(title="TechGap API")

# Allow local dev frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(curriculum.router)
app.include_router(job_role.router)
app.include_router(course_skill.router)
app.include_router(job_skill.router)
app.include_router(embedding.router)
app.include_router(match_result.router)
app.include_router(gap_report.router)
app.include_router(skill.router)
app.include_router(skill_match_detail.router)
app.include_router(gap_analysis.router)
app.include_router(predict.router, prefix="/predict", tags=["Predict"])


@app.get("/")
def root():
    return {"message": "Curriculum Gap Analyzer API is running"}
