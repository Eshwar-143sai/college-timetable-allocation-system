from fastapi import APIRouter
from app.api.v1.endpoints import faculty_router, subject_router, section_router, room_router, timetable_router, report_router

api_router = APIRouter()
api_router.include_router(faculty_router.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(subject_router.router, prefix="/courses", tags=["courses"])
api_router.include_router(section_router.router, prefix="/sections", tags=["sections"])
api_router.include_router(room_router.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(timetable_router.router, prefix="/timetable", tags=["timetable"])
api_router.include_router(report_router.router, prefix="/reports", tags=["reports"])
