# data_import2.py
"""
Optimized importer for the 4 generated CSVs:

- match_result.csv       -> match_result table
- skill_match_detail.csv -> skill_match_detail table
- gap_report.csv         -> gap_report table
- embedding.csv          -> embedding table

Features:
- Batch commits every BATCH_SIZE inserts
- Preloaded lookups for Curriculum, JobRole, Skill
- Duplicate skipping:
    * match_result: skip duplicate (curriculum_id, job_id, model)
    * gap_report:   skip duplicate (curriculum_id, missing_skill_id, recommendation, generated_by)
    * skill_match_detail: skip duplicate (curriculum_id, job_id, skill_id, model, status) in this run
    * embedding:    skip duplicate (owner_type, owner_id, model)
"""

import pandas as pd
from datetime import datetime

from app.database import SessionLocal
from app.models import (
    Curriculum,
    JobRole,
    Skill,
    Embedding,
    MatchResult,
    SkillMatchDetail,
    GapReport,
)

BATCH_SIZE = 500


# ============================================================
# Helper: parse ISO-ish datetime safely
# ============================================================

def _parse_datetime(value):
    """
    Parse datetime from CSV (ISO-like string) into Python datetime.
    Returns None if parsing fails or value is null/empty.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if not s:
        return None
    try:
        ts = pd.to_datetime(s, errors="coerce", utc=False)
        if pd.isna(ts):
            return None
        return ts.to_pydatetime()
    except Exception:
        return None


# ============================================================
# 1. IMPORT match_result.csv -> match_result table
# ============================================================

def import_match_results(csv_path: str = "match_result.csv"):
    """
    Import match_result.csv into match_result table.

    Mapping:
      - curriculum_track (string) -> Curriculum.track
      - job_title (string)        -> JobRole.title

    Handles:
      - Batch commits
      - In-run deduplication based on (curriculum_id, job_id, model)
    """
    df = pd.read_csv(csv_path)

    required_cols = {"curriculum_track", "job_title", "score", "rank_small", "model", "computed_at"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[import_match_results] Missing columns in {csv_path}: {missing}")

    db = SessionLocal()
    try:
        # Preload curriculum by track and jobs by title
        curricula_by_track = {}
        for cur in db.query(Curriculum).all():
            track_key = (cur.track or "").strip()
            if not track_key:
                continue
            curricula_by_track.setdefault(track_key, []).append(cur.curriculum_id)

        jobs_by_title = {}
        for job in db.query(JobRole).all():
            title_key = (job.title or "").strip()
            if not title_key:
                continue
            jobs_by_title.setdefault(title_key, []).append(job.job_id)

        created = 0
        skipped_missing = 0
        skipped_duplicate = 0
        pending = 0

        # Track (curriculum_id, job_id, model) seen in THIS run
        seen_keys = set()

        for _, row in df.iterrows():
            track_name = str(row["curriculum_track"]).strip()
            job_title = str(row["job_title"]).strip()
            score = float(row["score"])
            rank_small = int(row["rank_small"])
            model_name = str(row["model"]).strip()
            computed_at = _parse_datetime(row["computed_at"])

            if not track_name or not job_title:
                continue

            cur_ids = curricula_by_track.get(track_name)
            job_ids = jobs_by_title.get(job_title)

            if not cur_ids or not job_ids:
                skipped_missing += 1
                continue

            for cur_id in cur_ids:
                for job_id in job_ids:
                    key = (cur_id, job_id, model_name)

                    # Skip duplicate in this run
                    if key in seen_keys:
                        skipped_duplicate += 1
                        continue

                    seen_keys.add(key)

                    mr = MatchResult(
                        curriculum_id=cur_id,
                        job_id=job_id,
                        score=score,
                        rank_small=rank_small,
                        model=model_name,
                        computed_at=computed_at,
                    )
                    db.add(mr)
                    created += 1
                    pending += 1

                    if pending >= BATCH_SIZE:
                        db.commit()
                        pending = 0

        if pending > 0:
            db.commit()

        print(
            f"[import_match_results] Created {created} rows. "
            f"Skipped {skipped_missing} rows (no curriculum/job found). "
            f"Skipped {skipped_duplicate} duplicate (curriculum_id, job_id, model) rows in this run."
        )
    finally:
        db.close()


# ============================================================
# 2. IMPORT gap_report.csv -> gap_report table
# ============================================================

def import_gap_report(csv_path: str = "gap_report.csv"):
    """
    Import gap_report.csv into gap_report table.

    Mapping:
      - curriculum_track -> Curriculum.track
      - skill_name -> Skill.skill_id (can be NULL if not found)

    Duplicate logic:
      - Skip if (curriculum_id, missing_skill_id, recommendation, generated_by)
        already exists in DB or has been seen in this run.
    """
    df = pd.read_csv(csv_path)

    required_cols = {"curriculum_track", "skill_name", "recommendation", "generated_by", "date_generated"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[import_gap_report] Missing columns in {csv_path}: {missing}")

    db = SessionLocal()
    try:
        # Preload curriculum and skills
        curricula_by_track = {}
        for cur in db.query(Curriculum).all():
            track_key = (cur.track or "").strip()
            if not track_key:
                continue
            curricula_by_track.setdefault(track_key, []).append(cur.curriculum_id)

        skills_by_name = {}
        for sk in db.query(Skill).all():
            name_key = (sk.skill_name or "").strip().lower()
            if not name_key:
                continue
            skills_by_name[name_key] = sk.skill_id

        # Preload existing gap_report keys (in case table is not truncated)
        existing_keys = set(
            (gr.curriculum_id, gr.missing_skill_id, gr.recommendation, gr.generated_by)
            for gr in db.query(
                GapReport.curriculum_id,
                GapReport.missing_skill_id,
                GapReport.recommendation,
                GapReport.generated_by
            )
        )

        seen_keys = set()  # keys seen in THIS run

        created = 0
        skipped_missing_curr = 0
        skipped_duplicate = 0
        pending = 0

        for _, row in df.iterrows():
            track_name = str(row["curriculum_track"]).strip()
            skill_name_raw = (
                str(row["skill_name"]).strip().lower()
                if pd.notna(row["skill_name"])
                else ""
            )
            recommendation = str(row["recommendation"]).strip()
            generated_by = str(row["generated_by"]).strip()
            date_generated = _parse_datetime(row["date_generated"])

            if not track_name or not recommendation:
                continue

            cur_ids = curricula_by_track.get(track_name)
            if not cur_ids:
                skipped_missing_curr += 1
                continue

            missing_skill_id = None
            if skill_name_raw:
                missing_skill_id = skills_by_name.get(skill_name_raw)

            for cur_id in cur_ids:
                key = (cur_id, missing_skill_id, recommendation, generated_by)

                if key in existing_keys or key in seen_keys:
                    skipped_duplicate += 1
                    continue

                seen_keys.add(key)

                gr = GapReport(
                    curriculum_id=cur_id,
                    missing_skill_id=missing_skill_id,
                    recommendation=recommendation,
                    generated_by=generated_by,
                    date_generated=date_generated,
                )
                db.add(gr)
                created += 1
                pending += 1

                if pending >= BATCH_SIZE:
                    db.commit()
                    pending = 0

        if pending > 0:
            db.commit()

        print(
            f"[import_gap_report] Created {created} rows. "
            f"Skipped {skipped_missing_curr} rows (no curriculum found). "
            f"Skipped {skipped_duplicate} duplicate rows."
        )
    finally:
        db.close()


# ============================================================
# 3. IMPORT skill_match_detail.csv -> skill_match_detail table
# ============================================================

def import_skill_match_detail(csv_path: str = "skill_match_detail.csv"):
    """
    Import skill_match_detail.csv into skill_match_detail table.

    Mapping:
      - curriculum_track -> Curriculum.track
      - job_title -> JobRole.title
      - skill_name -> Skill.skill_id

    Duplicate logic:
      - Skip duplicates in THIS run based on
        (curriculum_id, job_id, skill_id, model, status).
      - We don't hit a DB unique constraint here, this is just
        to avoid bloating the table with duplicates.
    """
    df = pd.read_csv(csv_path)

    required_cols = {
        "curriculum_track",
        "job_title",
        "skill_name",
        "similarity_score",
        "status",
        "model",
        "computed_at",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[import_skill_match_detail] Missing columns in {csv_path}: {missing}")

    db = SessionLocal()
    try:
        # Preload curriculum, jobs, skills
        curricula_by_track = {}
        for cur in db.query(Curriculum).all():
            track_key = (cur.track or "").strip()
            if not track_key:
                continue
            curricula_by_track.setdefault(track_key, []).append(cur.curriculum_id)

        jobs_by_title = {}
        for job in db.query(JobRole).all():
            title_key = (job.title or "").strip()
            if not title_key:
                continue
            jobs_by_title.setdefault(title_key, []).append(job.job_id)

        skills_by_name = {}
        for sk in db.query(Skill).all():
            name_key = (sk.skill_name or "").strip().lower()
            if not name_key:
                continue
            skills_by_name[name_key] = sk.skill_id

        created = 0
        skipped_missing = 0
        skipped_duplicate = 0
        pending = 0

        seen_keys = set()  # (curriculum_id, job_id, skill_id, model, status)

        for _, row in df.iterrows():
            track_name = str(row["curriculum_track"]).strip()
            job_title = str(row["job_title"]).strip()
            skill_name_raw = str(row["skill_name"]).strip().lower()
            similarity_score = float(row["similarity_score"])
            status = str(row["status"]).strip()  # 'match', 'gap', 'partial'
            model_name = str(row["model"]).strip()
            computed_at = _parse_datetime(row["computed_at"])

            if not track_name or not job_title or not skill_name_raw:
                continue

            cur_ids = curricula_by_track.get(track_name)
            job_ids = jobs_by_title.get(job_title)
            skill_id = skills_by_name.get(skill_name_raw)

            if not cur_ids or not job_ids or not skill_id:
                skipped_missing += 1
                continue

            for cur_id in cur_ids:
                for job_id in job_ids:
                    key = (cur_id, job_id, skill_id, model_name, status)

                    if key in seen_keys:
                        skipped_duplicate += 1
                        continue

                    seen_keys.add(key)

                    smd = SkillMatchDetail(
                        curriculum_id=cur_id,
                        job_id=job_id,
                        skill_id=skill_id,
                        similarity_score=similarity_score,
                        status=status,
                        model=model_name,
                        computed_at=computed_at,
                    )
                    db.add(smd)
                    created += 1
                    pending += 1

                    if pending >= BATCH_SIZE:
                        db.commit()
                        pending = 0

        if pending > 0:
            db.commit()

        print(
            f"[import_skill_match_detail] Created {created} rows. "
            f"Skipped {skipped_missing} rows (missing curriculum/job/skill). "
            f"Skipped {skipped_duplicate} duplicate rows in this run."
        )
    finally:
        db.close()


# ============================================================
# 4. IMPORT embedding.csv -> embedding table
# ============================================================

def import_embeddings(csv_path: str = "embedding.csv"):
    """
    Import embedding.csv into embedding table.

    CSV:
        owner_type (job_role or curriculum_track or skill)
        owner_key  (job title, curriculum track name, or skill_name)
        model
        embedding_json
        vector_dim
        created_at (we *can* ignore and let DB default, but we map if present)

    DB:
        owner_type ENUM('curriculum','job_role','skill')
        owner_id   INT (FK)

    Duplicate logic:
      - Skip if (owner_type, owner_id, model) already exists in DB
        OR has been seen in this run.
    """
    df = pd.read_csv(csv_path)

    required_cols = {
        "owner_type",
        "owner_key",
        "model",
        "embedding_json",
        "vector_dim",
        "created_at",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[import_embeddings] Missing columns in {csv_path}: {missing}")

    db = SessionLocal()
    try:
        # Preload owners
        curricula_by_track = {}
        for cur in db.query(Curriculum).all():
            track_key = (cur.track or "").strip()
            if not track_key:
                continue
            curricula_by_track.setdefault(track_key, []).append(cur.curriculum_id)

        jobs_by_title = {}
        for job in db.query(JobRole).all():
            title_key = (job.title or "").strip()
            if not title_key:
                continue
            jobs_by_title.setdefault(title_key, []).append(job.job_id)

        skills_by_name = {}
        for sk in db.query(Skill).all():
            name_key = (sk.skill_name or "").strip().lower()
            if not name_key:
                continue
            skills_by_name[name_key] = sk.skill_id

        # Preload existing embeddings key (owner_type, owner_id, model)
        existing_keys = set(
            (emb.owner_type, emb.owner_id, emb.model)
            for emb in db.query(
                Embedding.owner_type,
                Embedding.owner_id,
                Embedding.model
            )
        )

        seen_keys = set()

        created = 0
        skipped_missing_owner = 0
        skipped_duplicate = 0
        pending = 0

        for _, row in df.iterrows():
            owner_type_raw = str(row["owner_type"]).strip()
            owner_key = str(row["owner_key"]).strip()
            model_name = str(row["model"]).strip()
            embedding_json = str(row["embedding_json"])
            vector_dim = int(row["vector_dim"])
            created_at = _parse_datetime(row["created_at"])

            if not owner_type_raw or not owner_key:
                continue

            if owner_type_raw == "job_role":
                db_owner_type = "job_role"
                key_title = owner_key.strip()
                owner_ids = jobs_by_title.get(key_title, [])
            elif owner_type_raw == "curriculum_track":
                db_owner_type = "curriculum"
                key_track = owner_key.strip()
                owner_ids = curricula_by_track.get(key_track, [])
            elif owner_type_raw == "skill":
                db_owner_type = "skill"
                owner_key_norm = owner_key.strip().lower()
                sk_id = skills_by_name.get(owner_key_norm)
                owner_ids = [sk_id] if sk_id is not None else []
            else:
                skipped_missing_owner += 1
                continue

            if not owner_ids:
                skipped_missing_owner += 1
                continue

            for owner_id in owner_ids:
                key = (db_owner_type, owner_id, model_name)

                if key in existing_keys or key in seen_keys:
                    skipped_duplicate += 1
                    continue

                seen_keys.add(key)

                emb = Embedding(
                    owner_type=db_owner_type,
                    owner_id=owner_id,
                    model=model_name,
                    embedding_json=embedding_json,
                    vector_dim=vector_dim,
                    created_at=created_at,
                )
                db.add(emb)
                created += 1
                pending += 1

                if pending >= BATCH_SIZE:
                    db.commit()
                    pending = 0

        if pending > 0:
            db.commit()

        print(
            f"[import_embeddings] Created {created} rows. "
            f"Skipped {skipped_missing_owner} rows (no owner found or unknown type). "
            f"Skipped {skipped_duplicate} duplicate embeddings."
        )
    finally:
        db.close()


# ============================================================
# 5. MAIN RUNNER
# ============================================================

if __name__ == "__main__":
    # You can comment/uncomment depending on what you want to run.
    # import_match_results("match_result.csv")
    # import_gap_report("gap_report.csv")
    #import_skill_match_detail("skill_match_detail.csv")
    import_embeddings("embedding.csv")

    print("All secondary CSV import steps completed.")