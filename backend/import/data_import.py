# data_import.py

import pandas as pd
from app.database import SessionLocal
from app.models import (
    Curriculum,
    JobRole,
    Skill,
    JobSkill,
    CourseSkill,
)

# ============================================================
# 1. IMPORT SKILLS FROM CLEANED CSVs -> skill table
# ============================================================

def import_skills_from_cleaned(
    course_skill_csv: str = "course_skill_cleaned.csv",
    job_skill_csv: str = "job_skill_with_query_cleaned_technical.csv",
):
    """
    Reads skill names from two cleaned CSVs and inserts unique skills into the Skill table.
    Mapping: 'skill name' (or similar) -> skill.skill_name
    """
    cs = pd.read_csv(course_skill_csv)
    js = pd.read_csv(job_skill_csv)

    # Try to detect the skill column name
    skill_cols_candidates = ["skill_name", "Skill", "skill", "skill name", "skill_name_cleaned"]

    def find_skill_col(df, label):
        for c in skill_cols_candidates:
            if c in df.columns:
                return c
        raise ValueError(f"No skill column found in {label}. Columns: {list(df.columns)}")

    cs_col = find_skill_col(cs, "course_skill_cleaned.csv")
    js_col = find_skill_col(js, "job_skill_with_query_cleaned_technical.csv")

    all_skills = pd.concat(
        [
            cs[cs_col].dropna().astype(str),
            js[js_col].dropna().astype(str),
        ],
        ignore_index=True,
    )

    # Normalize: strip, lowercase, drop duplicates
    all_skills = (
        all_skills
        .str.strip()
        .str.lower()
        .drop_duplicates()
    )

    db = SessionLocal()
    try:
        count_new = 0
        for name in all_skills:
            if not name:
                continue

            # Avoid inserting duplicates
            existing = db.query(Skill).filter(Skill.skill_name == name).first()
            if existing:
                continue

            skill = Skill(
                skill_name=name
            )

            db.add(skill)
            count_new += 1

        db.commit()
        print(f"[import_skills_from_cleaned] Imported {count_new} new skills.")
    finally:
        db.close()


# ============================================================
# 2. IMPORT CURRICULUM CSVs -> curriculum table
# ============================================================

def import_curriculum_track(csv_path: str, track_name: str):
    """
    Imports a single curriculum CSV into the Curriculum table.

    Mapping per row:
    - track_name (function argument) -> Curriculum.track
    - 'Course Title' -> Curriculum.course_title
    - 'Course Code'  -> Curriculum.course_code
    - 'Course Description' + ' ' + 'Outcome Text' -> Curriculum.raw_description
    """
    df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")

    title_col = "Course Title"
    code_col = "Course Code"
    desc_cols = [c for c in ["Course Description", "Outcome Text"] if c in df.columns]

    if title_col not in df.columns:
        raise ValueError(f"{csv_path} missing '{title_col}' column")

    db = SessionLocal()
    try:
        count = 0
        for _, row in df.iterrows():
            course_title = str(row.get(title_col, "")).strip()
            course_code = str(row.get(code_col, "")).strip() or None

            # description + " " + outcome text -> raw_description
            pieces = []
            for c in desc_cols:
                val = str(row.get(c, "")).strip()
                if val:
                    pieces.append(val)
            raw_description = " ".join(pieces) or None

            if not course_title and not raw_description:
                continue  # skip empty rows

            cur = Curriculum(
                track=track_name,
                course_title=course_title,
                course_code=course_code,
                raw_description=raw_description,
            )
            db.add(cur)
            count += 1

        db.commit()
        print(f"[import_curriculum_track] Imported {count} rows for track: {track_name}")
    finally:
        db.close()


def import_all_curriculum():
    """
    Calls import_curriculum_track for all four curriculum CSVs with the final track names:
    'CS Intelligent Systems',
    'CS Game Development',
    'IT Web Development',
    'IT Network Technology',
    """
    import_curriculum_track("CS IS CURRICULUM.csv",           "CS Intelligent Systems")
    import_curriculum_track("CS GAME DEV CURRICULUM.csv",     "CS Game Development")
    import_curriculum_track("IT Web Dev Curriculum.csv",      "IT Web Development")
    import_curriculum_track("IT Network Curriculum.csv",      "IT Network Technology")


# ============================================================
# 3. IMPORT JOBS -> job_role table
# ============================================================

def import_jobs_jobsdataset(csv_path: str = "JobsDataset.csv"):
    """
    Imports JobsDataset.csv into the JobRole table.

    Mapping per row:
    - 'Query'      -> JobRole.query
    - 'Job Title'  -> JobRole.title
    - 'Description'-> JobRole.profile_text
    """
    df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")

    expected_cols = {"Query", "Job Title", "Description"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"JobsDataset.csv missing columns: {missing}")

    db = SessionLocal()
    try:
        count = 0
        for _, row in df.iterrows():
            query = str(row["Query"]).strip()
            title = str(row["Job Title"]).strip()
            desc = str(row["Description"]).strip()

            if not title and not desc:
                continue  # skip completely empty rows

            job = JobRole(
                query=query or None,
                title=title,
                profile_text=desc,
            )
            db.add(job)
            count += 1

        db.commit()
        print(f"[import_jobs_jobsdataset] Imported {count} job roles.")
    finally:
        db.close()


# ============================================================
# 4. POPULATE job_skill & course_skill
# ============================================================

def populate_job_skill():
    """
    For each JobRole, scan profile_text for occurrences of each Skill.skill_name.
    When found, insert into job_skill (job_id, skill_id, importance).
    """
    db = SessionLocal()
    try:
        skills = db.query(Skill).all()
        jobs = db.query(JobRole).all()

        # Pre-lowercase skill names for faster search
        skill_list = [(s.skill_id, s.skill_name.lower()) for s in skills]

        count_links = 0
        for job in jobs:
            text = (job.profile_text or "").lower()
            if not text:
                continue

            for skill_id, skill_name in skill_list:
                if skill_name and skill_name in text:
                    # Check if link already exists to avoid duplicates
                    existing = db.query(JobSkill).filter_by(
                        job_id=job.job_id,
                        skill_id=skill_id
                    ).first()
                    if existing:
                        continue

                    link = JobSkill(
                        job_id=job.job_id,
                        skill_id=skill_id,
                    )

                    db.add(link)
                    count_links += 1

        db.commit()
        print(f"[populate_job_skill] Created {count_links} job_skill links.")
    finally:
        db.close()


def populate_course_skill():
    """
    For each Curriculum, scan raw_description for occurrences of each Skill.skill_name.
    When found, insert into course_skill (curriculum_id, skill_id, relevance).
    """
    db = SessionLocal()
    try:
        skills = db.query(Skill).all()
        curricula = db.query(Curriculum).all()

        skill_list = [(s.skill_id, s.skill_name.lower()) for s in skills]

        count_links = 0
        for cur in curricula:
            text = (cur.raw_description or "").lower()
            if not text:
                continue

            for skill_id, skill_name in skill_list:
                if skill_name and skill_name in text:
                    existing = db.query(CourseSkill).filter_by(
                        curriculum_id=cur.curriculum_id,
                        skill_id=skill_id
                    ).first()
                    if existing:
                        continue

                    link = CourseSkill(
                        curriculum_id=cur.curriculum_id,
                        skill_id=skill_id,
                    )

                    db.add(link)
                    count_links += 1

        db.commit()
        print(f"[populate_course_skill] Created {count_links} course_skill links.")
    finally:
        db.close()


# ============================================================
# 5. MAIN RUNNER
# ============================================================

if __name__ == "__main__":
    # You can comment/uncomment depending on what you want to run.

    # 1) Import curricula
    import_all_curriculum()

    # 2) Import jobs from JobsDataset
    import_jobs_jobsdataset()

    # 3) Import skills from the cleaned skill CSVs
    import_skills_from_cleaned()

    # 4) Populate job_skill and course_skill relationships
    populate_job_skill()
    populate_course_skill()

    print("All data import steps completed.")
