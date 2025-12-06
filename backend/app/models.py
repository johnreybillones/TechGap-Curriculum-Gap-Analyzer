from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# =========================
# 1. CURRICULUM
# =========================
class Curriculum(Base):
    __tablename__ = "curriculum"

    curriculum_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    track = Column(
        Enum(
            "CS Intelligent Systems",
            "CS Game Development",
            "IT Web Development",
            "IT Network Technology",
            "Other",
            name="curriculum_track_enum",
        ),
        nullable=False,
    )
    course_title = Column(String(255), nullable=False)
    course_code = Column(String(50), nullable=True)
    raw_description = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    course_skills = relationship("CourseSkill", back_populates="curriculum")
    match_results = relationship("MatchResult", back_populates="curriculum")
    gap_reports = relationship("GapReport", back_populates="curriculum")
    skill_match_details = relationship("SkillMatchDetail", back_populates="curriculum")


# =========================
# 2. JOB ROLE
# =========================
class JobRole(Base):
    __tablename__ = "job_role"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    query = Column(String(255), nullable=True)
    profile_text = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    job_skills = relationship("JobSkill", back_populates="job_role")
    match_results = relationship("MatchResult", back_populates="job_role")
    skill_match_details = relationship("SkillMatchDetail", back_populates="job_role")


# =========================
# 3. SKILL
# =========================
class Skill(Base):
    __tablename__ = "skill"

    skill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_name = Column(String(150), unique=True, nullable=False)
    # category column removed from DB, so remove it here as well
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    course_links = relationship("CourseSkill", back_populates="skill")
    job_links = relationship("JobSkill", back_populates="skill")
    gap_reports = relationship("GapReport", back_populates="missing_skill")
    skill_match_details = relationship("SkillMatchDetail", back_populates="skill")


# =========================
# 4. EMBEDDING
# =========================
class Embedding(Base):
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_type = Column(
        Enum("curriculum", "job_role", "skill", name="embedding_owner_type_enum"),
        nullable=False,
    )
    owner_id = Column(Integer, nullable=False)
    model = Column(String(100), nullable=False)
    embedding_json = Column(Text, nullable=False)
    vector_dim = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


# =========================
# 5. COURSE_SKILL (no relevance)
# =========================
class CourseSkill(Base):
    __tablename__ = "course_skill"

    curriculum_id = Column(
        Integer,
        ForeignKey("curriculum.curriculum_id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = Column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="CASCADE"),
        primary_key=True,
    )

    curriculum = relationship("Curriculum", back_populates="course_skills")
    skill = relationship("Skill", back_populates="course_links")


# =========================
# 6. JOB_SKILL (no importance)
# =========================
class JobSkill(Base):
    __tablename__ = "job_skill"

    job_id = Column(
        Integer,
        ForeignKey("job_role.job_id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = Column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="CASCADE"),
        primary_key=True,
    )

    job_role = relationship("JobRole", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_links")


# =========================
# 7. MATCH_RESULT
# =========================
class MatchResult(Base):
    __tablename__ = "match_result"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    curriculum_id = Column(
        Integer,
        ForeignKey("curriculum.curriculum_id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = Column(
        Integer,
        ForeignKey("job_role.job_id", ondelete="CASCADE"),
        nullable=False,
    )
    score = Column(Float, nullable=False)
    rank_small = Column(Integer, nullable=False)
    model = Column(String(100), nullable=False)
    computed_at = Column(DateTime, server_default=func.now(), nullable=False)

    curriculum = relationship("Curriculum", back_populates="match_results")
    job_role = relationship("JobRole", back_populates="match_results")


# =========================
# 8. SKILL_MATCH_DETAIL
# =========================
class SkillMatchDetail(Base):
    __tablename__ = "skill_match_detail"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(
        Integer,
        ForeignKey("curriculum.curriculum_id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = Column(
        Integer,
        ForeignKey("job_role.job_id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id = Column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="CASCADE"),
        nullable=False,
    )
    similarity_score = Column(Float, nullable=False)
    status = Column(
        Enum("match", "partial", "gap", name="skill_match_status_enum"),
        nullable=False,
    )
    model = Column(String(100), nullable=False)
    computed_at = Column(DateTime, server_default=func.now(), nullable=False)

    curriculum = relationship("Curriculum", back_populates="skill_match_details")
    job_role = relationship("JobRole", back_populates="skill_match_details")
    skill = relationship("Skill", back_populates="skill_match_details")


# =========================
# 9. GAP_REPORT
# =========================
class GapReport(Base):
    __tablename__ = "gap_report"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(
        Integer,
        ForeignKey("curriculum.curriculum_id", ondelete="CASCADE"),
        nullable=False,
    )
    missing_skill_id = Column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="SET NULL"),
        nullable=True,
    )
    recommendation = Column(Text, nullable=True)
    generated_by = Column(String(100), nullable=True)
    date_generated = Column(DateTime, server_default=func.now(), nullable=False)

    curriculum = relationship("Curriculum", back_populates="gap_reports")
    missing_skill = relationship("Skill", back_populates="gap_reports")
