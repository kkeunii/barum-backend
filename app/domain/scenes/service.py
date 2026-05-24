from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scenes.exceptions import SceneNotFoundException
from app.domain.scenes.models import Scene
from app.domain.scenes.repository import SceneRepository


class SceneService:
    """
    씬 Service.
    비즈니스 로직을 담당한다.
    """

    def __init__(self, db: AsyncSession):
        self.scene_repository = SceneRepository(db)

    async def get_scene(self, scene_id: int) -> Scene:
        scene = await self.scene_repository.get_active_scene_by_id(scene_id)

        if scene is None:
            raise SceneNotFoundException()

        return scene
