from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department_code = Column(String(10), nullable=False, unique=True, index=True)
    department_name = Column(String(100), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    faculties = relationship("Faculty", back_populates="department")
    courses = relationship("Course", back_populates="department")
