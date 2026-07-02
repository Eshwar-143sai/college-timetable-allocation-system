from app.schemas.user_schema import UserBase, UserCreate, UserResponse
from app.schemas.faculty_schema import (
    FacultyBase, FacultyCreate, FacultyUpdate, FacultyResponse,
    FacultyWorkloadResponse, FacultySubjectAssign, FacultySubjectResponse,
    FacultyDetailsResponse
)
from app.schemas.subject_schema import CourseBase, CourseCreate, CourseUpdate, CourseResponse
from app.schemas.section_schema import SectionBase, SectionCreate, SectionUpdate, SectionResponse
from app.schemas.room_schema import (
    ClassroomCreate, ClassroomUpdate, ClassroomResponse,
    LaboratoryCreate, LaboratoryUpdate, LaboratoryResponse
)
