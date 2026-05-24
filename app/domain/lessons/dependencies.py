from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domain.lessons.service import LessonService


def get_lesson_service(
    db: AsyncSession = Depends(get_db),
) -> LessonService:
    return LessonService(db)
