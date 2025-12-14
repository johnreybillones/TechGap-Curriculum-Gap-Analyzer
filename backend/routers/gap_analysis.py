import os
from dotenv import load_dotenv

from datetime import date
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database import SessionLocal

# Load .env from app directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')
load_dotenv(dotenv_path)
from app.models import (
    Curriculum,
    GapReport,
    JobRole,
    JobSkill,
    CourseSkill,
    MatchResult,
    Skill,
    SkillMatchDetail,
)

router = APIRouter(tags=["Gap Analysis"])

# In-memory caches
_OPTIONS_CACHE = None
_RECOMMENDATION_CACHE = {}  # Cache AI recommendations to reduce API calls

# --- CONFIGURATION: JOBS TO HIDE ---
BLACKLIST_JOBS = {
    "statistics",
    "business analyst",
    "data warehousing",
    "technology integration",
    "technical operations",
    "data architect",
    "machine learning",
    "deep learning",
    "business intelligence analyst",
    "data quality manager"
}

# -----------------------
# Helpers
# -----------------------
def invalidate_options_cache():
    global _OPTIONS_CACHE
    _OPTIONS_CACHE = None

def normalize_string(text: str) -> str:
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

# -----------------------
# Dependencies & Schemas
# -----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class GapAnalysisBase(BaseModel):
    course_id: int
    missing_skill_id: int
    recommendation: Optional[str] = None
    date_generated: Optional[date] = None

class GapAnalysisCreate(GapAnalysisBase):
    pass

class GapAnalysisOut(GapAnalysisBase):
    report_id: int
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    curriculum_id: int
    job_id: int


# -----------------------
# CORE LOGIC (DB Only)
# -----------------------

def _calculate_gap_analysis(curriculum_id: int, job_id: int, db: Session):
    # 1. Fetch Entities
    curriculum = db.query(Curriculum).filter(Curriculum.curriculum_id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail=f"Curriculum {curriculum_id} not found")

    job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

    # 2. Metrics Denominator: Total Skills in Curriculum
    total_curriculum_skills = db.query(func.count(CourseSkill.skill_id))\
        .filter(CourseSkill.curriculum_id == curriculum_id)\
        .scalar() or 0

    matches = []
    gaps = []
    
    # 3. Query SkillMatchDetail (Single Source of Truth)
    db_details = db.query(SkillMatchDetail, Skill.skill_name)\
        .join(Skill, SkillMatchDetail.skill_id == Skill.skill_id)\
        .filter(
            SkillMatchDetail.curriculum_id == curriculum_id,
            SkillMatchDetail.job_id == job_id
        ).all()

    # 4. Process Results
    if db_details:
        for row, skill_name in db_details:
            if row.status == 'match':
                matches.append(skill_name)
            else:
                gaps.append(skill_name)

    # 5. Calculate Metrics
    matches = sorted(list(set(matches)))
    gaps = sorted(list(set(gaps)))
    
    match_count = len(matches)
    gap_count = len(gaps)
    
    total_job_needs = match_count + gap_count
    
    # Avoid division by zero
    if total_curriculum_skills == 0:
        total_curriculum_skills = match_count if match_count > 0 else 1

    # Logic for Curriculum Relevance (Option B):
    # Relevance = (Skills Matched / Total Curriculum Skills)
    # Irrelevant = (Total Curriculum Skills - Skills Matched)
    irrelevant_count = max(0, total_curriculum_skills - match_count)

    coverage = (match_count / total_job_needs) if total_job_needs > 0 else 0.0
    relevance = (match_count / total_curriculum_skills) if total_curriculum_skills > 0 else 0.0
    if relevance > 1.0: relevance = 1.0
    
    return {
        "coverage": f"{coverage * 100:.1f}%",
        "relevance": f"{relevance * 100:.1f}%",
        "coverage_score": round(coverage * 100, 1),
        "relevance_score": round(relevance * 100, 1),
        
        # Counts
        "matchingSkills": match_count,
        "missingSkills": gap_count,
        "totalCurriculumSkills": total_curriculum_skills,
        "irrelevantSkills": irrelevant_count,
        
        # Detailed Lists
        "exact": matches,
        "gaps": gaps
    }


# -----------------------
# Analysis Endpoints
# -----------------------
@router.post("/api/analyze")
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    return _calculate_gap_analysis(request.curriculum_id, request.job_id, db)


# -----------------------
# Filtered Options Endpoint
# -----------------------
@router.get("/api/options")
def get_options(db: Session = Depends(get_db)):
    global _OPTIONS_CACHE
    if _OPTIONS_CACHE is not None:
        return _OPTIONS_CACHE

    # SUPER OPTIMIZED: Use pre-computed summary table (avoids 6M+ row scans)
    try:
        from sqlalchemy import text
        
        # Try to use summary table first (much faster)
        curricula_query = text("""
            SELECT entity_id as id, label 
            FROM options_summary 
            WHERE entity_type = 'curriculum'
            ORDER BY entity_id
        """)
        jobs_query = text("""
            SELECT entity_id as id, label 
            FROM options_summary 
            WHERE entity_type = 'job'
            ORDER BY entity_id
        """)
        
        curricula_rows = db.execute(curricula_query).fetchall()
        jobs_rows = db.execute(jobs_query).fetchall()
        
        # Deduplicate and filter
        curriculum_options = []
        seen_c = set()
        for row in curricula_rows:
            label = row.label or ""
            norm = normalize_string(label)
            if norm and norm not in seen_c:
                curriculum_options.append({"id": row.id, "label": label})
                seen_c.add(norm)
        
        job_options = []
        seen_j = set()
        for row in jobs_rows:
            label = row.label or ""
            if label.lower().strip() in BLACKLIST_JOBS:
                continue
            norm = normalize_string(label)
            if norm and norm not in seen_j:
                job_options.append({"id": row.id, "label": label})
                seen_j.add(norm)
        
        _OPTIONS_CACHE = {"curricula": curriculum_options, "jobs": job_options}
        return _OPTIONS_CACHE
        
    except Exception as e:
        # Fallback to JOIN query if summary table doesn't exist
        print(f"⚠️ Summary table not found, using slow fallback: {e}")
        
        curricula = db.query(Curriculum)\
            .join(SkillMatchDetail, Curriculum.curriculum_id == SkillMatchDetail.curriculum_id)\
            .distinct()\
            .order_by(Curriculum.curriculum_id)\
            .all()
        
        jobs = db.query(JobRole)\
            .join(SkillMatchDetail, JobRole.job_id == SkillMatchDetail.job_id)\
            .distinct()\
            .order_by(JobRole.job_id)\
            .all()

        curriculum_options = []
        seen_c = set()
        for c in curricula:
            label = c.track or c.course_title or ""
            norm = normalize_string(label)
            if norm and norm not in seen_c:
                curriculum_options.append({"id": c.curriculum_id, "label": label})
                seen_c.add(norm)
        
        job_options = []
        seen_j = set()
        for j in jobs:
            label = j.query or j.title or ""
            if label.lower().strip() in BLACKLIST_JOBS:
                continue
            norm = normalize_string(label)
            if norm and norm not in seen_j:
                job_options.append({"id": j.job_id, "label": label})
                seen_j.add(norm)

        _OPTIONS_CACHE = {"curricula": curriculum_options, "jobs": job_options}
        return _OPTIONS_CACHE

# ... (Keep the Debug and CRUD endpoints below this line exactly as they were in your file)


# -----------------------
# Debug Endpoints
# -----------------------
@router.get("/api/debug/detailed_skills_csv")
def debug_detailed_skills_csv(db: Session = Depends(get_db)):
    """
    Generate CSV file with detailed matched and gap skills for each curriculum-job combination
    """
    import csv
    from pathlib import Path
    from datetime import datetime
    
    print("\n" + "="*100)
    print(f"{'GENERATING DETAILED SKILLS CSV':^100}")
    print("="*100 + "\n")
    
    active_c_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.curriculum_id)).all()]
    active_j_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.job_id)).all()]

    curricula = db.query(Curriculum).filter(Curriculum.curriculum_id.in_(active_c_ids)).all()
    jobs = db.query(JobRole).filter(JobRole.job_id.in_(active_j_ids)).all()
    
    # Filter unique curricula
    unique_curricula = []
    seen = set()
    for c in curricula:
        key = normalize_string(c.track or c.course_title)
        if key not in seen:
            unique_curricula.append(c)
            seen.add(key)
    
    # Filter unique jobs
    unique_jobs = []
    seen_jobs = set()
    for j in jobs:
        label = (j.query or j.title or "").lower().strip()
        if label in BLACKLIST_JOBS:
            continue
        key = normalize_string(label)
        if key not in seen_jobs:
            unique_jobs.append(j)
            seen_jobs.add(key)

    # Prepare CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(__file__).resolve().parent.parent / "csvs" / f"detailed_skills_analysis_{timestamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    rows_written = 0
    
    with output_path.open('w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Curriculum_Name', 
            'Job_Title', 
            'Coverage', 'Relevance', 
            'Matches_Count', 'Gaps_Count',
            'Matched_Skills', 'Gap_Skills'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for c in unique_curricula:
            c_name = c.track or c.course_title or f"Curriculum {c.curriculum_id}"
            
            for j in unique_jobs:
                j_name = j.query or j.title or f"Job {j.job_id}"
                
                try:
                    res = _calculate_gap_analysis(c.curriculum_id, j.job_id, db)
                    
                    writer.writerow({
                        'Curriculum_Name': c_name,
                        'Job_Title': j_name,
                        'Coverage': res['coverage'],
                        'Relevance': res['relevance'],
                        'Matches_Count': res['matchingSkills'],
                        'Gaps_Count': res['missingSkills'],
                        'Matched_Skills': ', '.join(res['exact']) if res['exact'] else '',
                        'Gap_Skills': ', '.join(res['gaps']) if res['gaps'] else ''
                    })
                    rows_written += 1
                    
                except Exception as e:
                    print(f"ERROR: {c_name} vs {j_name}: {str(e)}")
    
    print(f"\n✅ CSV generated successfully!")
    print(f"   File: {output_path}")
    print(f"   Rows: {rows_written}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")
    print("="*100 + "\n")
    
    return {
        "message": "CSV file generated successfully",
        "file_path": str(output_path),
        "rows_written": rows_written,
        "curricula_count": len(unique_curricula),
        "jobs_count": len(unique_jobs)
    }


@router.get("/api/debug/detailed_skills")
def debug_detailed_skills(db: Session = Depends(get_db)):
    """
    Show detailed matched and gap skills for each curriculum-job combination
    """
    print("\n" + "="*100)
    print(f"{'DETAILED SKILLS ANALYSIS':^100}")
    print("="*100 + "\n")
    
    active_c_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.curriculum_id)).all()]
    active_j_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.job_id)).all()]

    curricula = db.query(Curriculum).filter(Curriculum.curriculum_id.in_(active_c_ids)).all()
    jobs = db.query(JobRole).filter(JobRole.job_id.in_(active_j_ids)).all()
    
    # Filter unique curricula
    unique_curricula = []
    seen = set()
    for c in curricula:
        key = normalize_string(c.track or c.course_title)
        if key not in seen:
            unique_curricula.append(c)
            seen.add(key)
    
    # Filter unique jobs
    unique_jobs = []
    seen_jobs = set()
    for j in jobs:
        label = (j.query or j.title or "").lower().strip()
        if label in BLACKLIST_JOBS:
            continue
        key = normalize_string(label)
        if key not in seen_jobs:
            unique_jobs.append(j)
            seen_jobs.add(key)

    print(f"Processing {len(unique_curricula)} unique curricula vs {len(unique_jobs)} unique jobs\n")
    
    full_report = []
    
    for i, c in enumerate(unique_curricula):
        c_name = c.track or c.course_title or f"Curriculum {c.curriculum_id}"
        print(f"\n{'='*100}")
        print(f"[{i+1}/{len(unique_curricula)}] CURRICULUM: {c_name} (ID: {c.curriculum_id})")
        print(f"{'='*100}\n")
        
        curriculum_results = []
        
        for j in unique_jobs:
            j_name = j.query or j.title or f"Job {j.job_id}"
            
            try:
                res = _calculate_gap_analysis(c.curriculum_id, j.job_id, db)
                
                # Print summary
                print(f"\n{'-'*100}")
                print(f"JOB: {j_name}")
                print(f"{'-'*100}")
                print(f"Coverage: {res['coverage']} | Relevance: {res['relevance']} | "
                      f"Matches: {res['matchingSkills']} | Gaps: {res['missingSkills']}")
                
                # Print matched skills
                print(f"\n✓ MATCHED SKILLS ({len(res['exact'])}):")
                if res['exact']:
                    print(f"  {', '.join(res['exact'])}")
                else:
                    print("  (none)")
                
                # Print gap skills
                print(f"\n✗ MISSING SKILLS ({len(res['gaps'])}):")
                if res['gaps']:
                    print(f"  {', '.join(res['gaps'])}")
                else:
                    print("  (none)")
                
                curriculum_results.append({
                    "job_title": j_name,
                    "job_id": j.job_id,
                    "metrics": {
                        "coverage": res['coverage'],
                        "relevance": res['relevance'],
                        "matchingSkills": res['matchingSkills'],
                        "missingSkills": res['missingSkills']
                    },
                    "matched_skills": res['exact'],
                    "gap_skills": res['gaps']
                })
                
            except Exception as e:
                print(f"\n{'-'*100}")
                print(f"JOB: {j_name}")
                print(f"{'-'*100}")
                print(f"ERROR: {str(e)}")
                curriculum_results.append({"job_title": j_name, "error": str(e)})
        
        full_report.append({
            "curriculum": c_name,
            "curriculum_id": c.curriculum_id,
            "results": curriculum_results
        })
    
    print(f"\n{'='*100}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*100}\n")
    
    return full_report


@router.get("/api/debug/full_matrix")
def debug_full_matrix(db: Session = Depends(get_db)):
    print("\n" + "="*80)
    print(f"{'FULL MATRIX GAP ANALYSIS':^80}")
    print("="*80 + "\n")
    
    active_c_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.curriculum_id)).all()]
    active_j_ids = [r[0] for r in db.query(distinct(SkillMatchDetail.job_id)).all()]

    curricula = db.query(Curriculum).filter(Curriculum.curriculum_id.in_(active_c_ids)).all()
    jobs = db.query(JobRole).filter(JobRole.job_id.in_(active_j_ids)).all()
    
    # Filter uniques for debug loop too
    unique_curricula = []
    seen = set()
    for c in curricula:
        key = normalize_string(c.track or c.course_title)
        if key not in seen:
            unique_curricula.append(c)
            seen.add(key)

    header = f"{'Job Title':<30} | {'Cov':<6} | {'Rel':<6} | {'Mat':<3} | {'Gap':<3}"
    
    for i, c in enumerate(unique_curricula):
        if i >= 4: break 
        
        c_name = c.track or c.course_title or f"Curriculum {c.curriculum_id}"
        total_width = 85
        title_with_spaces = f" {c_name} "
        padding = total_width - len(title_with_spaces)
        left_dashes = padding // 2
        right_dashes = padding - left_dashes
        print(f"{'-' * left_dashes}{title_with_spaces}{'-' * right_dashes}")
        print()
        print(f"{'Job Title':<30} | {'Job Coverage':<12} | {'Curriculum Relevance':<20} | {'Matches':<7} | {'Gaps':<4}")
        print("-" * 85)
        
        for j in jobs:
            # Skip blacklisted jobs in debug too (optional, keeps log clean)
            if (j.query or j.title or "").lower().strip() in BLACKLIST_JOBS:
                continue

            j_name = j.query or j.title or f"Job {j.job_id}"
            try:
                res = _calculate_gap_analysis(c.curriculum_id, j.job_id, db)
                print(f"{j_name:<30} | {res['coverage']:<12} | {res['relevance']:<20} | {res['matchingSkills']:<7} | {res['missingSkills']:<4}")
            except Exception as e:
                # pass silently
                pass
        print("\n")

    return []


# -----------------------
# CRUD Operations
# -----------------------
@router.post("/gapanalysis", response_model=GapAnalysisOut)
def create_report(data: GapAnalysisCreate, db: Session = Depends(get_db)):
    new_report = GapReport(**data.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/gapanalysis", response_model=List[GapAnalysisOut])
def get_reports(db: Session = Depends(get_db)):
    return db.query(GapReport).all()

@router.get("/gapanalysis/{report_id}", response_model=GapAnalysisOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    return report

@router.put("/gapanalysis/{report_id}", response_model=GapAnalysisOut)
def update_report(report_id: int, data: GapAnalysisBase, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    for key, value in data.dict().items(): setattr(report, key, value)
    db.commit()
    return report

@router.delete("/gapanalysis/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GapReport).filter(GapReport.report_id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail="Not found")
    db.delete(report)
    db.commit()
    return {"message": "Deleted"}

class RecommendationRequest(BaseModel):
    job_title: str
    curriculum_title: str
    missing_skills: List[str]
    coverage_score: float
    relevance_score: float

@router.post("/api/recommend")
def generate_recommendation(request: RecommendationRequest):
    # Lazy import to avoid slowing down startup
    import google.generativeai as genai
    
    # Check cache first (reduces API calls significantly)
    cache_key = f"{request.curriculum_title}_{request.job_title}_{request.coverage_score}_{request.relevance_score}"
    if cache_key in _RECOMMENDATION_CACHE:
        print(f"✓ Returning cached recommendation for {request.curriculum_title} vs {request.job_title}")
        return {"recommendation": _RECOMMENDATION_CACHE[cache_key]}
    
    # Check if API key is present
    if not os.getenv("GOOGLE_API_KEY"):
        return {"recommendation": "⚠️ API Key missing. Please set GOOGLE_API_KEY in your backend environment."}
    
    # Configure Gemini on first use (lazy initialization)
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Limit skills to avoid token overflow
    skills_list = ", ".join(request.missing_skills[:15])
    
    # --- CONCISE PROMPT FOR STUDENTS & PROFESSORS ---
    prompt = f"""
    You are a curriculum advisor for CICS analyzing gap between "{request.curriculum_title}" and "{request.job_title}" roles.

    Job Coverage Score: {request.coverage_score}%
    Curriculum Relevance Score: {request.relevance_score}%
    Top Missing Skills: {skills_list}

    Provide a response in this EXACT format:

**Job Coverage Analysis ({request.coverage_score}%):**
[Write paragraph here - 3-4 sentences explaining: what this score means, which technical categories are covered vs missing, and root cause. Use transition words. Bold only the 2-3 most critical missing skills or gaps.]

**Curriculum Relevance Analysis ({request.relevance_score}%):**
[Write paragraph here - 3-4 sentences explaining: what this score reveals, which topics are relevant vs less applicable, and why. Use transition words. Bold only the 2-3 most important technical areas needing updates.]

**Top 3 Actions:**
- **[Action Verb]** [specific, actionable technical recommendation]
- **[Action Verb]** [specific, actionable technical recommendation]  
- **[Action Verb]** [specific, actionable technical recommendation]

CRITICAL FORMATTING:
- Use exactly **two asterisks** before and after bold text
- In paragraphs: Bold only 2-3 most critical technical terms per section
- In actions: Bold only the action verb at the start of each bullet
- Do NOT add blank lines anywhere
    """
    # -------------------------------------------------------
    
    last_error = None
    
    # STRATEGY: Groq first (fastest), then Gemini as backup
    
    # ═══════════════════════════════════════════════════════════════
    # TIER 1: GROQ API (Primary - Fast & Reliable)
    # ═══════════════════════════════════════════════════════════════
    
    # 1. Groq (Llama 3.3 70B - Very fast, 30 req/min = 43,200/day, truly free)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            print("🚀 Trying Groq API (Llama 3.3 70B - fastest inference)...")
            import requests
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 600
                },
                timeout=10
            )
            
            if response.ok:
                text = response.json()["choices"][0]["message"]["content"]
                _RECOMMENDATION_CACHE[cache_key] = text
                print("✅ Groq API succeeded!")
                return {"recommendation": text}
        except Exception as e:
            last_error = e
            print(f"⚠️ Groq API failed: {str(e)[:100]}...")
    
    # ═══════════════════════════════════════════════════════════════
    # TIER 2: GEMINI (Backup - has quota limits but good quality)
    # ═══════════════════════════════════════════════════════════════
    
    if os.getenv("GOOGLE_API_KEY"):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        GEMINI_MODELS = [
            'gemini-2.5-flash-lite',         # Fastest, separate quota pool
            'gemini-2.5-flash',              # Balanced performance
            'gemini-2.5-pro',                # Most capable
            'gemini-2.0-flash-lite',         # Older lite version
            'gemini-2.0-flash',              # Older flash version
            'gemini-flash-lite-latest',      # Latest lite alias
            'gemini-flash-latest',           # Latest flash alias
            'gemini-pro-latest',             # Latest pro alias
        ]
        
        for model_name in GEMINI_MODELS:
            try:
                if hasattr(genai, "GenerativeModel"):
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    
                    # Check if response was blocked by safety filters
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        if hasattr(response.prompt_feedback, 'block_reason'):
                            print(f"⚠️ {model_name} blocked content (safety filters), trying next model...")
                            continue
                    
                    # Try to extract text from response
                    text = None
                    if hasattr(response, 'text'):
                        try:
                            text = response.text
                        except:
                            pass
                    
                    if not text and hasattr(response, 'candidates') and response.candidates:
                        try:
                            text = response.candidates[0].content.parts[0].text
                        except:
                            pass
                    
                    if text:
                        _RECOMMENDATION_CACHE[cache_key] = text
                        print(f"✅ {model_name} succeeded!")
                        return {"recommendation": text}
                    else:
                        print(f"⚠️ {model_name} returned empty response, trying next model...")
                        continue
                        
            except Exception as e:
                error_msg = str(e).lower()
                last_error = e
                
                # Check for quota/rate limit errors
                if any(keyword in error_msg for keyword in ['quota', 'limit', 'rate', 'resource_exhausted', '429']):
                    print(f"⚠️ {model_name} quota exceeded, trying next model...")
                    continue
                else:
                    print(f"⚠️ {model_name} error: {str(e)[:100]}... Trying next model...")
                    continue
    
    # All APIs failed
    print(f"❌ All 10 models failed. Last error: {last_error}")
    return {"recommendation": "Unable to generate AI recommendations at this time. All models are currently unavailable. Please try again later."}

# Clear cache endpoint (useful for testing or when cache gets stale)
@router.post("/api/recommend/clear-cache")
def clear_recommendation_cache():
    global _RECOMMENDATION_CACHE
    cache_size = len(_RECOMMENDATION_CACHE)
    _RECOMMENDATION_CACHE = {}
    return {"message": f"Cleared {cache_size} cached recommendations"}
