from fastapi import APIRouter, Depends

from app.domain.scenes.dependencies import get_scene_service
from app.domain.scenes.service import SceneService

router = APIRouter(tags=["scenes"])


@router.get("/{scene_id}")
async def get_scene(
    scene_id: str,
    scene_service: SceneService = Depends(get_scene_service),
):
    return await scene_service.get_scene(scene_id)


@router.get("/{scene_id}/utterances")
async def get_scene_utterances(
    scene_id: str,
    scene_service: SceneService = Depends(get_scene_service),
):
    return await scene_service.get_scene_utterances(scene_id)
