from app.domain.utterances.service import UtteranceService
from app.domain.utterances.exceptions import SceneNotFoundException
from app.domain.scenes.schemas import SceneResponse


class SceneService:
    def __init__(self):
        self.utterance_service = UtteranceService()

    async def get_scene(self, scene_id: str) -> SceneResponse:
        return self.utterance_service.get_scene(scene_id)

    async def get_scene_utterances(self, scene_id: str) -> list[object]:
        return self.utterance_service.get_scene_utterances(scene_id)
