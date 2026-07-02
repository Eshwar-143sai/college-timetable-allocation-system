from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, Text
from app.database.base_class import Base

class Classroom(Base):
    __tablename__ = "classrooms"
    
    classroom_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(20), nullable=False, unique=True, index=True)
    building = Column(String(50), nullable=False)
    floor = Column(SmallInteger, nullable=False)
    capacity = Column(Integer, nullable=False)
    has_projector = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)

class Laboratory(Base):
    __tablename__ = "laboratories"
    
    lab_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lab_number = Column(String(20), nullable=False, unique=True, index=True)
    building = Column(String(50), nullable=False)
    floor = Column(SmallInteger, nullable=False)
    capacity = Column(Integer, nullable=False)
    lab_type = Column(String(50), nullable=False)
    equipment_details = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
