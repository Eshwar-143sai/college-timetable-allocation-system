from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database.session import get_db
from app.models.section import Section
from app.models.department import Department
from app.models.faculty import Faculty
from app.schemas.section_schema import SectionCreate, SectionUpdate, SectionResponse

router = APIRouter()

def format_section_name_with_dept(db: Session, name: str, dept_id: int) -> str:
    dept = db.query(Department).filter(Department.department_id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )
        
    prefix = f"{dept.department_code}-"
    name_upper = name.upper().strip()
    
    if name_upper.startswith(prefix):
        return name_upper
    else:
        # If they input just "A", convert to "CSE-A"
        return f"{dept.department_code}-{name_upper}"

@router.get("/", response_model=List[SectionResponse])
def list_sections(
    department_id: Optional[int] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    academic_year: str = Query("2025-2026", description="Filter by academic year"),
    db: Session = Depends(get_db)
):
    query = db.query(Section).filter(Section.academic_year == academic_year)
    
    if department_id:
        query = query.filter(Section.department_id == department_id)
    if semester:
        query = query.filter(Section.semester == semester)
        
    return query.all()

@router.get("/{section_id}", response_model=SectionResponse)
def get_section(section_id: int, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.section_id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return section

@router.post("/", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(section_in: SectionCreate, db: Session = Depends(get_db)):
    # 1. Format section name (e.g. "A" -> "CSE-A")
    formatted_name = format_section_name_with_dept(db, section_in.section_name, section_in.department_id)
    
    # 2. Check uniqueness
    existing = db.query(Section).filter(
        Section.section_name == formatted_name,
        Section.academic_year == section_in.academic_year
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Section '{formatted_name}' already exists for academic year {section_in.academic_year}"
        )
        
    # 3. Check advisor
    if section_in.class_advisor_id:
        advisor = db.query(Faculty).filter(Faculty.faculty_id == section_in.class_advisor_id).first()
        if not advisor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty advisor with ID {section_in.class_advisor_id} not found"
            )
            
    # 4. Create section
    section = Section(
        section_name=formatted_name,
        department_id=section_in.department_id,
        semester=section_in.semester,
        academic_year=section_in.academic_year,
        student_strength=section_in.student_strength,
        class_advisor_id=section_in.class_advisor_id
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    
    return section

@router.put("/{section_id}", response_model=SectionResponse)
def update_section(section_id: int, section_in: SectionUpdate, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.section_id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
        
    # Determine department and section name
    dept_id = section_in.department_id if section_in.department_id is not None else section.department_id
    
    # Check advisor
    if section_in.class_advisor_id is not None:
        advisor = db.query(Faculty).filter(Faculty.faculty_id == section_in.class_advisor_id).first()
        if not advisor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty advisor not found"
            )
            
    # Check department
    if section_in.department_id is not None:
        dept = db.query(Department).filter(Department.department_id == section_in.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # Format name if updated or if department changed
    if section_in.section_name is not None or section_in.department_id is not None:
        name_to_format = section_in.section_name if section_in.section_name is not None else section.section_name
        formatted_name = format_section_name_with_dept(db, name_to_format, dept_id)
        
        # Check uniqueness if name changed
        acad_year = section_in.academic_year if section_in.academic_year is not None else section.academic_year
        if formatted_name != section.section_name or acad_year != section.academic_year:
            existing = db.query(Section).filter(
                Section.section_name == formatted_name,
                Section.academic_year == acad_year,
                Section.section_id != section_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Section '{formatted_name}' already exists for academic year {acad_year}"
                )
            
            section.section_name = formatted_name

    # Update other fields
    update_data = section_in.dict(exclude={"section_name"}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)
        
    db.commit()
    db.refresh(section)
    
    return section

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(section_id: int, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.section_id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
        
    db.delete(section)
    db.commit()
    return None
