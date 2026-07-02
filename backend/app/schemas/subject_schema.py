from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class DepartmentMini(BaseModel):
    department_id: int
    department_code: str
    department_name: str

    class Config:
        from_attributes = True

class FacultyMini(BaseModel):
    faculty_id: int
    employee_code: str
    first_name: str
    last_name: str
    designation: str

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    course_code: str = Field(..., max_length=15)
    course_name: str = Field(..., max_length=150)
    department_id: int
    course_type: str  # 'Theory', 'Lab', 'Theory+Lab'
    semester: int
    is_active: Optional[bool] = True

class CourseCreate(CourseBase):
    lecture_hours: int = Field(0, ge=0)
    tutorial_hours: int = Field(0, ge=0)
    practical_hours: int = Field(0, ge=0)
    self_study_hours: int = Field(0, ge=0)
    credits: Decimal = Field(..., gt=0)
    
    # Optional initial faculty assignments
    assigned_faculty_ids: Optional[List[int]] = []
    academic_year: Optional[str] = "2025-2026"

class CourseUpdate(BaseModel):
    course_code: Optional[str] = Field(None, max_length=15)
    course_name: Optional[str] = Field(None, max_length=150)
    department_id: Optional[int] = None
    course_type: Optional[str] = None
    semester: Optional[int] = None
    is_active: Optional[bool] = None
    
    lecture_hours: Optional[int] = Field(None, ge=0)
    tutorial_hours: Optional[int] = Field(None, ge=0)
    practical_hours: Optional[int] = Field(None, ge=0)
    self_study_hours: Optional[int] = Field(None, ge=0)
    credits: Optional[Decimal] = Field(None, gt=0)
    
    assigned_faculty_ids: Optional[List[int]] = None
    academic_year: Optional[str] = "2025-2026"

class CourseResponse(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    department_id: int
    course_type: str
    semester: int
    is_active: bool
    
    # Resolved LTPSC values
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    self_study_hours: int
    credits: Decimal
    
    department: Optional[DepartmentMini] = None
    assigned_faculty: List[FacultyMini] = []

    class Config:
        from_attributes = True
