from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Section(Base):
    __tablename__ = "sections"
    
    section_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section_name = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    semester = Column(Integer, nullable=False)
    academic_year = Column(String(9), nullable=False)
    student_strength = Column(Integer, default=0)
    class_advisor_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('section_name', 'academic_year', name='uq_section_year'),
    )
    
    # Relationships
    department = relationship("Department")
    advisor = relationship("Faculty", backref="sections_advised")
