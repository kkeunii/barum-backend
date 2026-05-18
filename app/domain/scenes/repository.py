from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scenes.models import Scene


class SceneRepository:
    """
    씬 Repository.
    DB 접근만 담당한다.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_scene_by_id(self, scene_id: int) -> Optional[Scene]:
        stmt = select(Scene).where(
            Scene.scenes_id == scene_id,
            Scene.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
