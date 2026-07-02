from sqlalchemy import Column, Integer, String, Enum, ForeignKey, TIMESTAMP, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Faculty(Base):
    __tablename__ = "faculty"
    
    faculty_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    employee_code = Column(String(20), nullable=False, unique=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    designation = Column(
        Enum("Professor", "Associate Professor", "Assistant Professor", "Lecturer"), 
        nullable=False
    )
    max_hours_per_week = Column(Integer, default=18)
    phone = Column(String(15), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    user = relationship("User", back_populates="faculty")
    department = relationship("Department", back_populates="faculties")
    faculty_subjects = relationship("FacultySubject", back_populates="faculty", cascade="all, delete-orphan")
    workloads = relationship("FacultyWorkload", back_populates="faculty", cascade="all, delete-orphan")

class FacultyWorkload(Base):
    __tablename__ = "faculty_workload"
    
    workload_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., '2025-2026'
    semester = Column(Integer, nullable=False)
    total_hours_assigned = Column(Integer, default=0)
    max_hours_allowed = Column(Integer, nullable=False)
    updated_at = Column(
        TIMESTAMP, 
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    
    __table_args__ = (
        UniqueConstraint('faculty_id', 'academic_year', 'semester', name='uq_workload_faculty_term'),
    )
    
    # Relationships
    faculty = relationship("Faculty", back_populates="workloads")
