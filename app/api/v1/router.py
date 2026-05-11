from fastapi import APIRouter

from app.domain.attempts.router import router as attempts_router
from app.domain.lessons.router import router as lessons_router
from app.domain.scenes.router import router as scenes_router
from app.domain.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(
    lessons_router,
    prefix="/lessons",
    tags=["lessons"],
)

api_router.include_router(
    scenes_router,
    prefix="/scenes",
    tags=["scenes"],
)

api_router.include_router(
    attempts_router,
    prefix="/attempts",
    tags=["attempts"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)
