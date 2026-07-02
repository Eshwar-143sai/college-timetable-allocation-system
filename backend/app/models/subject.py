from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, Numeric, TIMESTAMP, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Ltpsc(Base):
    __tablename__ = "ltpsc"
    
    ltpsc_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lecture_hours = Column(Integer, default=0, nullable=False)
    tutorial_hours = Column(Integer, default=0, nullable=False)
    practical_hours = Column(Integer, default=0, nullable=False)
    self_study_hours = Column(Integer, default=0, nullable=False)
    credits = Column(Numeric(3, 1), nullable=False)
    
    __table_args__ = (
        UniqueConstraint(
            'lecture_hours', 'tutorial_hours', 'practical_hours', 'self_study_hours', 'credits',
            name='uq_ltpsc_pattern'
        ),
    )
    
    # Relationships
    courses = relationship("Course", back_populates="ltpsc")

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_code = Column(String(15), nullable=False, unique=True, index=True)
    course_name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    ltpsc_id = Column(Integer, ForeignKey("ltpsc.ltpsc_id"), nullable=False)
    course_type = Column(Enum("Theory", "Lab", "Theory+Lab"), nullable=False)
    semester = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    department = relationship("Department", back_populates="courses")
    ltpsc = relationship("Ltpsc", back_populates="courses")
    faculty_subjects = relationship("FacultySubject", back_populates="course", cascade="all, delete-orphan")

class FacultySubject(Base):
    __tablename__ = "faculty_subject"
    
    faculty_subject_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., '2025-2026'
    
    __table_args__ = (
        UniqueConstraint('faculty_id', 'course_id', 'academic_year', name='uq_faculty_course_year'),
    )
    
    # Relationships
    faculty = relationship("Faculty", back_populates="faculty_subjects")
    course = relationship("Course", back_populates="faculty_subjects")
