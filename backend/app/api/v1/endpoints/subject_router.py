from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from decimal import Decimal

from app.database.session import get_db
from app.models.subject import Course, Ltpsc, FacultySubject
from app.models.faculty import Faculty, FacultyWorkload
from app.models.department import Department
from app.schemas.subject_schema import CourseCreate, CourseUpdate, CourseResponse, FacultyMini
from app.services.faculty_service import recalculate_faculty_workload

router = APIRouter()

def get_or_create_ltpsc(
    db: Session, 
    lecture: int, 
    tutorial: int, 
    practical: int, 
    self_study: int, 
    credits: Decimal
) -> Ltpsc:
    # Look for existing LTPSC pattern
    ltpsc = db.query(Ltpsc).filter(
        Ltpsc.lecture_hours == lecture,
        Ltpsc.tutorial_hours == tutorial,
        Ltpsc.practical_hours == practical,
        Ltpsc.self_study_hours == self_study,
        Ltpsc.credits == credits
    ).first()
    
    if not ltpsc:
        # Create new pattern
        ltpsc = Ltpsc(
            lecture_hours=lecture,
            tutorial_hours=tutorial,
            practical_hours=practical,
            self_study_hours=self_study,
            credits=credits
        )
        db.add(ltpsc)
        db.commit()
        db.refresh(ltpsc)
        
    return ltpsc

def format_course_response(db: Session, course: Course, academic_year: str = "2025-2026") -> CourseResponse:
    # Fetch ltpsc details
    ltpsc = course.ltpsc
    
    # Fetch assigned faculty members
    assigned_raw = (
        db.query(Faculty)
        .join(FacultySubject, Faculty.faculty_id == FacultySubject.faculty_id)
        .filter(
            FacultySubject.course_id == course.course_id,
            FacultySubject.academic_year == academic_year
        )
        .all()
    )
    
    assigned_faculty = [
        FacultyMini(
            faculty_id=f.faculty_id,
            employee_code=f.employee_code,
            first_name=f.first_name,
            last_name=f.last_name,
            designation=f.designation
        ) for f in assigned_raw
    ]
    
    return CourseResponse(
        course_id=course.course_id,
        course_code=course.course_code,
        course_name=course.course_name,
        department_id=course.department_id,
        course_type=course.course_type,
        semester=course.semester,
        is_active=course.is_active,
        lecture_hours=ltpsc.lecture_hours,
        tutorial_hours=ltpsc.tutorial_hours,
        practical_hours=ltpsc.practical_hours,
        self_study_hours=ltpsc.self_study_hours,
        credits=ltpsc.credits,
        department=course.department,
        assigned_faculty=assigned_faculty
    )

@router.get("/", response_model=List[CourseResponse])
def list_courses(
    search: Optional[str] = Query(None, description="Search by name or course code"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    course_type: Optional[str] = Query(None, description="Filter by course type"),
    academic_year: str = Query("2025-2026", description="Academic year to fetch faculty assignments for"),
    db: Session = Depends(get_db)
):
    query = db.query(Course)
    
    if department_id:
        query = query.filter(Course.department_id == department_id)
    if semester:
        query = query.filter(Course.semester == semester)
    if course_type:
        query = query.filter(Course.course_type == course_type)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Course.course_name.like(search_filter),
                Course.course_code.like(search_filter)
            )
        )
        
    courses = query.all()
    return [format_course_response(db, c, academic_year) for c in courses]

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int, 
    academic_year: str = Query("2025-2026", description="Academic year to fetch faculty assignments for"),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return format_course_response(db, course, academic_year)

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course_in: CourseCreate, db: Session = Depends(get_db)):
    # 1. Check code uniqueness
    existing = db.query(Course).filter(Course.course_code == course_in.course_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with code {course_in.course_code} already exists"
        )
        
    # 2. Check department
    dept = db.query(Department).filter(Department.department_id == course_in.department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {course_in.department_id} not found"
        )
        
    # 3. Get or create LTPSC pattern
    ltpsc = get_or_create_ltpsc(
        db,
        lecture=course_in.lecture_hours,
        tutorial=course_in.tutorial_hours,
        practical=course_in.practical_hours,
        self_study=course_in.self_study_hours,
        credits=course_in.credits
    )
    
    # 4. Create course
    course = Course(
        course_code=course_in.course_code,
        course_name=course_in.course_name,
        department_id=course_in.department_id,
        ltpsc_id=ltpsc.ltpsc_id,
        course_type=course_in.course_type,
        semester=course_in.semester,
        is_active=course_in.is_active
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # 5. Handle initial faculty assignments
    if course_in.assigned_faculty_ids:
        for fac_id in course_in.assigned_faculty_ids:
            fac = db.query(Faculty).filter(Faculty.faculty_id == fac_id).first()
            if not fac:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Faculty member with ID {fac_id} not found"
                )
            
            fac_sub = FacultySubject(
                faculty_id=fac_id,
                course_id=course.course_id,
                academic_year=course_in.academic_year
            )
            db.add(fac_sub)
        db.commit()
        
        # Recalculate workloads for assigned faculty
        for fac_id in course_in.assigned_faculty_ids:
            recalculate_faculty_workload(db, fac_id, course_in.academic_year, course.semester)
            
    return format_course_response(db, course, course_in.academic_year)

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_in: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
        
    # Check department
    if course_in.department_id is not None:
        dept = db.query(Department).filter(Department.department_id == course_in.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
            
    # Check code uniqueness
    if course_in.course_code is not None and course_in.course_code != course.course_code:
        existing = db.query(Course).filter(Course.course_code == course_in.course_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with code {course_in.course_code} already exists"
            )
            
    # Resolve LTPSC if hours/credits are updated
    original_ltpsc = course.ltpsc
    lecture = course_in.lecture_hours if course_in.lecture_hours is not None else original_ltpsc.lecture_hours
    tutorial = course_in.tutorial_hours if course_in.tutorial_hours is not None else original_ltpsc.tutorial_hours
    practical = course_in.practical_hours if course_in.practical_hours is not None else original_ltpsc.practical_hours
    self_study = course_in.self_study_hours if course_in.self_study_hours is not None else original_ltpsc.self_study_hours
    credits = course_in.credits if course_in.credits is not None else original_ltpsc.credits
    
    ltpsc = get_or_create_ltpsc(db, lecture, tutorial, practical, self_study, credits)
    course.ltpsc_id = ltpsc.ltpsc_id
    
    # Store previous details for workload recalculations
    old_semester = course.semester
    
    # Update other course fields
    update_data = course_in.dict(exclude={"lecture_hours", "tutorial_hours", "practical_hours", "self_study_hours", "credits", "assigned_faculty_ids", "academic_year"}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
        
    db.commit()
    db.refresh(course)
    
    # Track faculty who need workload recalculation
    faculty_to_recalculate = set()
    
    # Fetch faculty currently linked to this course (for the academic year)
    current_links = db.query(FacultySubject).filter(
        FacultySubject.course_id == course_id,
        FacultySubject.academic_year == course_in.academic_year
    ).all()
    
    current_faculty_ids = {link.faculty_id for link in current_links}
    
    # If assigned_faculty_ids is specified, sync them
    if course_in.assigned_faculty_ids is not None:
        target_faculty_ids = set(course_in.assigned_faculty_ids)
        
        # Faculty to remove
        to_remove = current_faculty_ids - target_faculty_ids
        # Faculty to add
        to_add = target_faculty_ids - current_faculty_ids
        
        # Add affected faculty to recalculation set
        faculty_to_recalculate.update(current_faculty_ids)
        faculty_to_recalculate.update(target_faculty_ids)
        
        # Delete links for removed faculty
        if to_remove:
            db.query(FacultySubject).filter(
                FacultySubject.course_id == course_id,
                FacultySubject.academic_year == course_in.academic_year,
                FacultySubject.faculty_id.in_(to_remove)
            ).delete(synchronize_session=False)
            
        # Add links for new faculty
        for fac_id in to_add:
            fac = db.query(Faculty).filter(Faculty.faculty_id == fac_id).first()
            if not fac:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Faculty member with ID {fac_id} not found"
                )
            fac_sub = FacultySubject(
                faculty_id=fac_id,
                course_id=course_id,
                academic_year=course_in.academic_year
            )
            db.add(fac_sub)
            
        db.commit()
    else:
        # If faculty list wasn't modified, but hours or semester changed, recalculate all currently assigned faculty
        faculty_to_recalculate.update(current_faculty_ids)
        
    # Recalculate workloads
    for fac_id in faculty_to_recalculate:
        # Recalculate for new semester
        recalculate_faculty_workload(db, fac_id, course_in.academic_year, course.semester)
        # If semester changed, also recalculate for old semester to subtract workload
        if old_semester != course.semester:
            recalculate_faculty_workload(db, fac_id, course_in.academic_year, old_semester)
            
    return format_course_response(db, course, course_in.academic_year)

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int, 
    academic_year: str = Query("2025-2026", description="Academic year of assignments to clean up"),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
        
    semester = course.semester
    
    # Get all faculty members currently assigned to this course
    assigned_links = db.query(FacultySubject).filter(
        FacultySubject.course_id == course_id,
        FacultySubject.academic_year == academic_year
    ).all()
    
    assigned_faculty_ids = [link.faculty_id for link in assigned_links]
    
    # Delete course (cascades will delete FacultySubject table rows)
    db.delete(course)
    db.commit()
    
    # Recalculate workloads for affected faculty members
    for fac_id in assigned_faculty_ids:
        recalculate_faculty_workload(db, fac_id, academic_year, semester)
        
    return None

@router.get("/helper/faculty", response_model=List[FacultyMini])
def list_faculty_helpers(db: Session = Depends(get_db)):
    faculties = db.query(Faculty).all()
    return faculties
