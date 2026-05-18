from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SceneResponse(BaseModel):
    """
    씬 응답 DTO.
    """

    scenes_id: int
    lesson_id: int
    order_index: int
    sentence: str
    video_url: str
    audio_url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonSceneResponse(BaseModel):
    """
    레슨 상세 응답에 포함되는 씬 DTO.
    """

    scenes_id: int
    order_index: int
    sentence: str
    video_url: str
    audio_url: str

    model_config = ConfigDict(from_attributes=True)
