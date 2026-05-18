from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domain.scenes.service import SceneService


def get_scene_service(
    db: AsyncSession = Depends(get_db),
) -> SceneService:
    return SceneService(db)
