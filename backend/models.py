from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Course(Base):
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_code = Column(String(20), nullable=False)
    course_name = Column(String(100), nullable=False)
    description = Column(Text)
    department = Column(String(100))

    skills = relationship("CourseSkill", back_populates="course")


class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)

    course_links = relationship("CourseSkill", back_populates="skill")
    job_links = relationship("JobSkill", back_populates="skill")


class JobPosting(Base):
    __tablename__ = "jobpostings"
    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_title = Column(String(100), nullable=False)
    company = Column(String(100))
    description = Column(Text, nullable=False)
    source = Column(String(50))
    date_posted = Column(Date)

    skills = relationship("JobSkill", back_populates="job")


class CourseSkill(Base):
    __tablename__ = "courseskills"
    course_id = Column(Integer, ForeignKey("courses.course_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), primary_key=True)
    relevance_level = Column(Integer, nullable=False)

    __table_args__ = (CheckConstraint('relevance_level BETWEEN 1 AND 5'),)

    course = relationship("Course", back_populates="skills")
    skill = relationship("Skill", back_populates="course_links")


class JobSkill(Base):
    __tablename__ = "jobskills"
    job_id = Column(Integer, ForeignKey("jobpostings.job_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), primary_key=True)
    importance_level = Column(Integer, nullable=False)

    __table_args__ = (CheckConstraint('importance_level BETWEEN 1 AND 5'),)

    job = relationship("JobPosting", back_populates="skills")
    skill = relationship("Skill", back_populates="job_links")


class GapAnalysis(Base):
    __tablename__ = "gapanalysis"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    missing_skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    recommendation = Column(Text)
    date_generated = Column(Date)

    course = relationship("Course")
    missing_skill = relationship("Skill")
