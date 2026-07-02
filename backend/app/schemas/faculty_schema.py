from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Basic schemas for reference
class DepartmentMini(BaseModel):
    department_id: int
    department_code: str
    department_name: str

    class Config:
        from_attributes = True

class UserMini(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class FacultyBase(BaseModel):
    employee_code: str = Field(..., max_length=20)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    department_id: int
    designation: str  # 'Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer'
    phone: Optional[str] = Field(None, max_length=15)

class FacultyCreate(FacultyBase):
    # Optional credentials for automatically creating user login
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class FacultyUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    department_id: Optional[int] = None
    designation: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=15)

class FacultyWorkloadResponse(BaseModel):
    workload_id: int
    faculty_id: int
    academic_year: str
    semester: int
    total_hours_assigned: int
    max_hours_allowed: int
    updated_at: datetime

    class Config:
        from_attributes = True

class FacultyResponse(BaseModel):
    faculty_id: int
    user_id: int
    employee_code: str
    first_name: str
    last_name: str
    department_id: int
    designation: str
    max_hours_per_week: int
    phone: Optional[str]
    created_at: datetime
    
    # Nested information
    user: Optional[UserMini] = None
    department: Optional[DepartmentMini] = None

    class Config:
        from_attributes = True

# Subject Assignment Schema
class FacultySubjectAssign(BaseModel):
    course_id: int
    academic_year: str  # e.g., '2025-2026'

class FacultySubjectResponse(BaseModel):
    faculty_subject_id: int
    faculty_id: int
    course_id: int
    academic_year: str
    
    # Detail on the course
    course_code: str
    course_name: str
    course_type: str
    semester: int
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    credits: Decimal

    class Config:
        from_attributes = True
        
class FacultyDetailsResponse(BaseModel):
    faculty: FacultyResponse
    workloads: List[FacultyWorkloadResponse] = []
    subjects: List[FacultySubjectResponse] = []
