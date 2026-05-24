from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.lessons.exceptions import LessonNotFoundException
from app.domain.lessons.models import Lesson
from app.domain.lessons.repository import LessonRepository


class LessonService:
    """
    레슨 Service.
    비즈니스 로직을 담당한다.
    """

    def __init__(self, db: AsyncSession):
        self.lesson_repository = LessonRepository(db)

    async def get_lessons(self) -> list[Lesson]:
        return await self.lesson_repository.get_active_lessons()

    async def get_lesson(self, lesson_id: int) -> Lesson:
        lesson = await self.lesson_repository.get_active_lesson_with_scenes_by_id(
            lesson_id,
        )

        if lesson is None:
            raise LessonNotFoundException()

        return lesson
