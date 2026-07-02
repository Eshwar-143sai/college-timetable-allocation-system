from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.schemas.subject_schema import DepartmentMini, FacultyMini

class SectionBase(BaseModel):
    section_name: str = Field(..., max_length=20, description="Section identifier e.g. A, B, C or CSE-A")
    department_id: int
    semester: int = Field(..., ge=1, le=8)
    academic_year: str = Field("2025-2026", max_length=9)
    student_strength: int = Field(0, ge=0)
    class_advisor_id: Optional[int] = None

    @field_validator("section_name")
    @classmethod
    def validate_section_name(cls, v: str) -> str:
        val = v.upper().strip()
        parts = val.split('-')
        last_part = parts[-1]
        valid_sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        if last_part not in valid_sections:
            raise ValueError(f"Section name must end with one of {valid_sections} (e.g. A or CSE-A)")
        return val

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    section_name: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    semester: Optional[int] = Field(None, ge=1, le=8)
    academic_year: Optional[str] = Field(None, max_length=9)
    student_strength: Optional[int] = Field(None, ge=0)
    class_advisor_id: Optional[int] = None

    @field_validator("section_name")
    @classmethod
    def validate_section_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        val = v.upper().strip()
        parts = val.split('-')
        last_part = parts[-1]
        valid_sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        if last_part not in valid_sections:
            raise ValueError(f"Section name must end with one of {valid_sections} (e.g. A or CSE-A)")
        return val

class SectionResponse(BaseModel):
    section_id: int
    section_name: str
    department_id: int
    semester: int
    academic_year: str
    student_strength: int
    class_advisor_id: Optional[int] = None
    
    department: Optional[DepartmentMini] = None
    advisor: Optional[FacultyMini] = None

    class Config:
        from_attributes = True
