from fastapi import APIRouter

from app.domain.lessons.router import router as lessons_router
from app.domain.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(
    lessons_router,
    prefix="/lessons",
    tags=["lessons"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)
