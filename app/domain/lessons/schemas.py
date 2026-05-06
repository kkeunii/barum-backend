from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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
