import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import time

from app.database.base_class import Base
from app.main import app
from app.database.session import get_db
from app.models.user import User
from app.models.department import Department
from app.models.faculty import Faculty
from app.models.section import Section
from app.models.room import Classroom, Laboratory
from app.models.subject import Ltpsc, Course, FacultySubject
from app.models.timetable import TimeSlot

# File-based SQLite Database for test runs to avoid `:memory:` connection isolation issues
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates an isolated database schema, seeds default reference entities, 
    yields a session, and drops all tables at the end of the test.
    """
    # SQLite compatibility adjustment: strip MySQL-specific ON UPDATE clause from metadata
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if column.server_default and hasattr(column.server_default, "arg"):
                arg_str = str(column.server_default.arg)
                if "ON UPDATE CURRENT_TIMESTAMP" in arg_str:
                    from sqlalchemy.sql.schema import DefaultClause
                    column.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))

    # Remove test.db file if exists to start fresh
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass

    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Seed reference data
        # 1. Department
        dept = Department(department_id=1, department_name="Computer Science", department_code="CSE")
        db.add(dept)
        db.commit()
        
        # 2. User
        usr = User(
            user_id=1,
            username="johndoe",
            email="john.doe@college.edu",
            password_hash="some_hash",
            role="faculty",
            is_active=True
        )
        db.add(usr)
        db.commit()
        
        # 3. Faculty
        fac = Faculty(
            faculty_id=1,
            user_id=1,
            employee_code="FAC101",
            first_name="John",
            last_name="Doe",
            designation="Professor",
            department_id=1,
            max_hours_per_week=12
        )
        db.add(fac)
        db.commit()
        
        # 4. Section
        sec = Section(
            section_id=1,
            section_name="CSE-A",
            department_id=1,
            semester=3,
            academic_year="2025-2026",
            student_strength=60
        )
        db.add(sec)
        db.commit()
        
        # 5. Rooms
        room = Classroom(
            classroom_id=1,
            room_number="A-101",
            building="Block A",
            floor=1,
            capacity=70,
            has_projector=True,
            is_available=True
        )
        lab = Laboratory(
            lab_id=1,
            lab_number="L-301",
            building="Block C",
            floor=3,
            capacity=40,
            lab_type="Computer Lab",
            is_available=True
        )
        db.add_all([room, lab])
        db.commit()
        
        # 6. LTPSC & Course
        ltpsc = Ltpsc(ltpsc_id=1, lecture_hours=3, tutorial_hours=1, practical_hours=0, self_study_hours=2, credits=4)
        db.add(ltpsc)
        db.commit()
        
        course = Course(
            course_id=1,
            course_code="CS301",
            course_name="Database Systems",
            course_type="Theory",
            semester=3,
            department_id=1,
            ltpsc_id=1,
            is_active=True
        )
        db.add(course)
        db.commit()
        
        # Faculty assignment
        assignment = FacultySubject(
            faculty_id=1,
            course_id=1,
            academic_year="2025-2026"
        )
        db.add(assignment)
        db.commit()
        
        # 7. Time Slots (Monday Periods 1-4)
        slots = [
            TimeSlot(slot_id=1, day_of_week="Monday", start_time=time(9, 0), end_time=time(10, 0), slot_order=1),
            TimeSlot(slot_id=2, day_of_week="Monday", start_time=time(10, 0), end_time=time(11, 0), slot_order=2),
            TimeSlot(slot_id=3, day_of_week="Monday", start_time=time(11, 15), end_time=time(12, 15), slot_order=3),
            TimeSlot(slot_id=4, day_of_week="Monday", start_time=time(12, 15), end_time=time(13, 15), slot_order=4)
        ]
        db.add_all(slots)
        db.commit()
        
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        # Clean up database file after run
        if os.path.exists("./test.db"):
            try:
                os.remove("./test.db")
            except Exception:
                pass

@pytest.fixture(scope="function")
def client(db_session):
    """
    Overloads FastAPI database dependency injection to use the test session 
    and yields a TestClient.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
