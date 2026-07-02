from fastapi import APIRouter
from app.api.v1.endpoints import faculty_router

api_router = APIRouter()
api_router.include_router(faculty_router.router, prefix="/faculty", tags=["faculty"])
