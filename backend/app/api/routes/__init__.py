from fastapi import APIRouter

from app.api.routes import admin, auth, quiz

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(quiz.router, tags=["quiz"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
