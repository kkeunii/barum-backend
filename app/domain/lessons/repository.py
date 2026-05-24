from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.domain.lessons.models import Lesson
from app.domain.scenes.models import Scene


class LessonRepository:
    """
    레슨 Repository.
    DB 접근만 담당한다.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_lessons(self) -> list[Lesson]:
        stmt = (
            select(Lesson)
            .where(Lesson.is_active.is_(True))
            .order_by(Lesson.lessons_id.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        stmt = select(Lesson).where(
            Lesson.lessons_id == lesson_id,
            Lesson.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_lesson_with_scenes_by_id(
        self,
        lesson_id: int,
    ) -> Optional[Lesson]:
        stmt = (
            select(Lesson)
            .options(
                selectinload(Lesson.scenes),
                with_loader_criteria(Scene, Scene.is_active.is_(True)),
            )
            .where(
                Lesson.lessons_id == lesson_id,
                Lesson.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
