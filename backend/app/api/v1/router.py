from fastapi import APIRouter

from app.api.v1.endpoints import health, reports, scores, students, subjects

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scores.router, prefix="/scores", tags=["scores"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
