from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SceneResponse(BaseModel):
    scene_id: str
    scene_name: str
    lesson_id: str
    lesson_name: str
    utterance_count: int

    model_config = ConfigDict(from_attributes=True)
