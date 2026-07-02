from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Time, Boolean, TIMESTAMP, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    slot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_of_week = Column(
        Enum("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"), 
        nullable=False
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_order = Column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('day_of_week', 'start_time', name='uq_slot_day_start'),
    )

class Timetable(Base):
    __tablename__ = "timetable"
    
    timetable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.slot_id"), nullable=False)
    academic_year = Column(String(9), nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    __table_args__ = (
        UniqueConstraint('section_id', 'slot_id', 'academic_year', name='uq_timetable_section_slot'),
        UniqueConstraint('faculty_id', 'slot_id', 'academic_year', name='uq_timetable_faculty_slot'),
    )
    
    # Relationships
    section = relationship("Section")
    course = relationship("Course")
    faculty = relationship("Faculty")
    slot = relationship("TimeSlot")
    room_allocation = relationship("RoomAllocation", back_populates="timetable", uselist=False, cascade="all, delete-orphan")

class RoomAllocation(Base):
    __tablename__ = "room_allocation"
    
    room_allocation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timetable_id = Column(Integer, ForeignKey("timetable.timetable_id"), nullable=False, unique=True)
    room_type = Column(Enum("Classroom", "Laboratory"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.classroom_id"), nullable=True)
    lab_id = Column(Integer, ForeignKey("laboratories.lab_id"), nullable=True)
    
    # Relationships
    timetable = relationship("Timetable", back_populates="room_allocation")
    classroom = relationship("Classroom")
    lab = relationship("Laboratory")

class ConstraintModel(Base):
    __tablename__ = "constraints_table"
    
    constraint_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    constraint_type = Column(
        Enum("Faculty_Unavailability", "Room_Unavailability", "Preferred_Slot", "Section_Break"), 
        nullable=False
    )
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.classroom_id"), nullable=True)
    lab_id = Column(Integer, ForeignKey("laboratories.lab_id"), nullable=True)
    slot_id = Column(Integer, ForeignKey("time_slots.slot_id"), nullable=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    faculty = relationship("Faculty")
    classroom = relationship("Classroom")
    lab = relationship("Laboratory")
    slot = relationship("TimeSlot")
