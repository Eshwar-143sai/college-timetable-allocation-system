from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.faculty import Faculty, FacultyWorkload
from app.models.subject import FacultySubject, Course, Ltpsc
from app.models.user import User
from app.auth.password_utils import get_password_hash  # We will implement this simple helper

def get_max_hours_by_designation(designation: str) -> int:
    mapping = {
        "Professor": 12,
        "Associate Professor": 14,
        "Assistant Professor": 16,
        "Lecturer": 18
    }
    return mapping.get(designation, 18)

def recalculate_faculty_workload(db: Session, faculty_id: int, academic_year: str, semester: int) -> FacultyWorkload:
    # 1. Fetch faculty to get designation
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise ValueError("Faculty not found")
        
    max_hours = get_max_hours_by_designation(faculty.designation)
    
    # 2. Get all courses assigned to this faculty for the given academic year
    # Join with Course and Ltpsc to filter by semester and get teaching hours
    assigned_courses = (
        db.query(Ltpsc.lecture_hours, Ltpsc.tutorial_hours, Ltpsc.practical_hours)
        .select_from(FacultySubject)
        .join(Course, FacultySubject.course_id == Course.course_id)
        .join(Ltpsc, Course.ltpsc_id == Ltpsc.ltpsc_id)
        .filter(
            FacultySubject.faculty_id == faculty_id,
            FacultySubject.academic_year == academic_year,
            Course.semester == semester
        )
        .all()
    )
    
    # 3. Sum the contact hours (L + T + P)
    total_hours = sum(
        (lh + th + ph) for lh, th, ph in assigned_courses
    )
    
    # 4. Check if workload record already exists
    workload = db.query(FacultyWorkload).filter(
        FacultyWorkload.faculty_id == faculty_id,
        FacultyWorkload.academic_year == academic_year,
        FacultyWorkload.semester == semester
    ).first()
    
    if workload:
        workload.total_hours_assigned = total_hours
        workload.max_hours_allowed = max_hours
    else:
        workload = FacultyWorkload(
            faculty_id=faculty_id,
            academic_year=academic_year,
            semester=semester,
            total_hours_assigned=total_hours,
            max_hours_allowed=max_hours
        )
        db.add(workload)
        
    db.commit()
    db.refresh(workload)
    return workload

def recalculate_all_workloads_for_faculty(db: Session, faculty_id: int):
    # Find all unique academic year and semester assignments for this faculty
    assignments = (
        db.query(FacultySubject.academic_year, Course.semester)
        .join(Course, FacultySubject.course_id == Course.course_id)
        .filter(FacultySubject.faculty_id == faculty_id)
        .distinct()
        .all()
    )
    
    for academic_year, semester in assignments:
        recalculate_faculty_workload(db, faculty_id, academic_year, semester)
        
    # Also update max hours allowed for existing workloads if designation changed
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if faculty:
        max_hours = get_max_hours_by_designation(faculty.designation)
        workloads = db.query(FacultyWorkload).filter(FacultyWorkload.faculty_id == faculty_id).all()
        for wl in workloads:
            wl.max_hours_allowed = max_hours
        db.commit()
