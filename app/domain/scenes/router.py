from fastapi import APIRouter, Depends

from app.domain.scenes.dependencies import get_scene_service
from app.domain.scenes.schemas import SceneResponse
from app.domain.scenes.service import SceneService

router = APIRouter()


@router.get(
    "/{scene_id}",
    response_model=SceneResponse,
)
async def get_scene(
    scene_id: int,
    scene_service: SceneService = Depends(get_scene_service),
):
    """
    씬 단건 조회 API.
    """

    return await scene_service.get_scene(scene_id)
