from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.scenes.schemas import LessonSceneResponse


class LessonResponse(BaseModel):
    """
    레슨 응답 DTO.
    """

    lessons_id: int
    title: str
    description: Optional[str]
    difficulty: str
    thumbnail_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonDetailResponse(LessonResponse):
    """
    레슨 상세 응답 DTO.
    레슨에 포함된 씬 목록을 함께 내려준다.
    """

    scenes: list[LessonSceneResponse]
