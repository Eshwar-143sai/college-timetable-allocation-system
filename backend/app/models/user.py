from sqlalchemy import Column, Integer, String, Enum, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "hod", "faculty", "student"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP, 
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    
    # Relationships
    faculty = relationship("Faculty", back_populates="user", uselist=False, cascade="all, delete-orphan")
