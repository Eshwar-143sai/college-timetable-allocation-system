from fastapi import APIRouter
from app.api.v1.endpoints import faculty_router, subject_router, section_router

api_router = APIRouter()
api_router.include_router(faculty_router.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(subject_router.router, prefix="/courses", tags=["courses"])
api_router.include_router(section_router.router, prefix="/sections", tags=["sections"])
