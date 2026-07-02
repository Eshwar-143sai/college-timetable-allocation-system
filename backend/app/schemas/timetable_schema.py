from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TimetableValidationRequest(BaseModel):
    section_id: int
    course_id: int
    faculty_id: int
    slot_id: int
    room_id: int
    room_type: str = Field(..., description="Must be 'Classroom' or 'Laboratory'")
    academic_year: str = Field("2025-2026")
    current_timetable_id: Optional[int] = None

class TimetableValidationResponse(BaseModel):
    is_valid: bool
    conflicts: List[Dict[str, Any]]
