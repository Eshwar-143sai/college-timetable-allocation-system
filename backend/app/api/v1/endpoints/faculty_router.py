from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database.session import get_db
from app.models.faculty import Faculty, FacultyWorkload
from app.models.user import User
from app.models.department import Department
from app.models.subject import Course, FacultySubject, Ltpsc
from app.schemas.faculty_schema import (
    FacultyCreate, FacultyUpdate, FacultyResponse,
    FacultySubjectAssign, FacultySubjectResponse, FacultyDetailsResponse
)
from app.services.faculty_service import (
    recalculate_faculty_workload, 
    recalculate_all_workloads_for_faculty,
    get_max_hours_by_designation
)
from app.auth.password_utils import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[FacultyResponse])
def list_faculty(
    search: Optional[str] = Query(None, description="Search by name, employee code, or designation"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    query = db.query(Faculty)
    
    if department_id:
        query = query.filter(Faculty.department_id == department_id)
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Faculty.first_name.like(search_filter),
                Faculty.last_name.like(search_filter),
                Faculty.employee_code.like(search_filter),
                Faculty.designation.like(search_filter)
            )
        )
        
    return query.all()

@router.get("/{faculty_id}", response_model=FacultyDetailsResponse)
def get_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Faculty member not found"
        )
        
    # Get Workloads
    workloads = db.query(FacultyWorkload).filter(FacultyWorkload.faculty_id == faculty_id).all()
    
    # Get Subjects
    subjects_raw = (
        db.query(
            FacultySubject.faculty_subject_id,
            FacultySubject.faculty_id,
            FacultySubject.course_id,
            FacultySubject.academic_year,
            Course.course_code,
            Course.course_name,
            Course.course_type,
            Course.semester,
            Ltpsc.lecture_hours,
            Ltpsc.tutorial_hours,
            Ltpsc.practical_hours,
            Ltpsc.credits
        )
        .join(Course, FacultySubject.course_id == Course.course_id)
        .join(Ltpsc, Course.ltpsc_id == Ltpsc.ltpsc_id)
        .filter(FacultySubject.faculty_id == faculty_id)
        .all()
    )
    
    subjects = [
        FacultySubjectResponse(
            faculty_subject_id=s.faculty_subject_id,
            faculty_id=s.faculty_id,
            course_id=s.course_id,
            academic_year=s.academic_year,
            course_code=s.course_code,
            course_name=s.course_name,
            course_type=s.course_type,
            semester=s.semester,
            lecture_hours=s.lecture_hours,
            tutorial_hours=s.tutorial_hours,
            practical_hours=s.practical_hours,
            credits=s.credits
        ) for s in subjects_raw
    ]
    
    return FacultyDetailsResponse(
        faculty=faculty,
        workloads=workloads,
        subjects=subjects
    )

@router.post("/", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
def create_faculty(faculty_in: FacultyCreate, db: Session = Depends(get_db)):
    # 1. Validate employee code uniqueness
    existing_faculty = db.query(Faculty).filter(Faculty.employee_code == faculty_in.employee_code).first()
    if existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faculty with employee code {faculty_in.employee_code} already exists"
        )
        
    # 2. Check department
    dept = db.query(Department).filter(Department.department_id == faculty_in.department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {faculty_in.department_id} not found"
        )
        
    # 3. Create User account
    if not faculty_in.username or not faculty_in.email or not faculty_in.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username, email, and password are required to create a faculty login account"
        )
        
    # Check if username or email is already taken
    existing_user = db.query(User).filter(
        or_(User.username == faculty_in.username, User.email == faculty_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered"
        )
        
    # Hash password and create User
    hashed_pwd = get_password_hash(faculty_in.password)
    user = User(
        username=faculty_in.username,
        email=faculty_in.email,
        password_hash=hashed_pwd,
        role="faculty"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 4. Create Faculty linked to User
    max_hours = get_max_hours_by_designation(faculty_in.designation)
    faculty = Faculty(
        user_id=user.user_id,
        employee_code=faculty_in.employee_code,
        first_name=faculty_in.first_name,
        last_name=faculty_in.last_name,
        department_id=faculty_in.department_id,
        designation=faculty_in.designation,
        max_hours_per_week=max_hours,
        phone=faculty_in.phone
    )
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    
    return faculty

@router.put("/{faculty_id}", response_model=FacultyResponse)
def update_faculty(faculty_id: int, faculty_in: FacultyUpdate, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Faculty member not found"
        )
        
    # Check if department exists
    if faculty_in.department_id is not None:
        dept = db.query(Department).filter(Department.department_id == faculty_in.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
            
    # Update fields
    update_data = faculty_in.dict(exclude_unset=True)
    
    # If designation is modified, recalculate max hours
    if "designation" in update_data:
        max_hours = get_max_hours_by_designation(update_data["designation"])
        faculty.max_hours_per_week = max_hours
        
    for field, value in update_data.items():
        setattr(faculty, field, value)
        
    db.commit()
    db.refresh(faculty)
    
    # Recalculate all workload records for this faculty to update max allowed hours
    recalculate_all_workloads_for_faculty(db, faculty_id)
    
    return faculty

@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Faculty member not found"
        )
        
    # Cascades will handle FacultyWorkload, FacultySubject deletion.
    # We must delete the associated User login account.
    user = db.query(User).filter(User.user_id == faculty.user_id).first()
    
    db.delete(faculty)
    if user:
        db.delete(user)
        
    db.commit()
    return None

@router.post("/{faculty_id}/assign-subject", response_model=FacultySubjectResponse)
def assign_subject(
    faculty_id: int, 
    assignment: FacultySubjectAssign, 
    db: Session = Depends(get_db)
):
    # Check if faculty exists
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Faculty member not found"
        )
        
    # Check if course exists
    course = db.query(Course).filter(Course.course_id == assignment.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course/Subject not found"
        )
        
    # Check if already assigned
    existing = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == faculty_id,
        FacultySubject.course_id == assignment.course_id,
        FacultySubject.academic_year == assignment.academic_year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This course is already assigned to the faculty for the specified academic year"
        )
        
    # Create assignment
    fac_sub = FacultySubject(
        faculty_id=faculty_id,
        course_id=assignment.course_id,
        academic_year=assignment.academic_year
    )
    db.add(fac_sub)
    db.commit()
    db.refresh(fac_sub)
    
    # Recalculate workload automatically for this semester and year
    recalculate_faculty_workload(db, faculty_id, assignment.academic_year, course.semester)
    
    # Fetch detail response
    ltpsc = db.query(Ltpsc).filter(Ltpsc.ltpsc_id == course.ltpsc_id).first()
    
    return FacultySubjectResponse(
        faculty_subject_id=fac_sub.faculty_subject_id,
        faculty_id=fac_sub.faculty_id,
        course_id=fac_sub.course_id,
        academic_year=fac_sub.academic_year,
        course_code=course.course_code,
        course_name=course.course_name,
        course_type=course.course_type,
        semester=course.semester,
        lecture_hours=ltpsc.lecture_hours,
        tutorial_hours=ltpsc.tutorial_hours,
        practical_hours=ltpsc.practical_hours,
        credits=ltpsc.credits
    )

@router.delete("/{faculty_id}/unassign-subject/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_subject(
    faculty_id: int, 
    course_id: int, 
    academic_year: str = Query(..., description="Academic year of the assignment to remove"),
    db: Session = Depends(get_db)
):
    fac_sub = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == faculty_id,
        FacultySubject.course_id == course_id,
        FacultySubject.academic_year == academic_year
    ).first()
    
    if not fac_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject assignment not found for this faculty, course, and academic year"
        )
        
    # Get course details to know semester for workload recalculation
    course = db.query(Course).filter(Course.course_id == course_id).first()
    semester = course.semester if course else None
    
    db.delete(fac_sub)
    db.commit()
    
    # Recalculate workload
    if semester:
        recalculate_faculty_workload(db, faculty_id, academic_year, semester)
        
    return None

@router.get("/helper/departments")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return [{"department_id": d.department_id, "department_code": d.department_code, "department_name": d.department_name} for d in depts]

@router.get("/helper/courses")
def list_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.is_active == True).all()
    return [{"course_id": c.course_id, "course_code": c.course_code, "course_name": c.course_name, "semester": c.semester} for c in courses]
