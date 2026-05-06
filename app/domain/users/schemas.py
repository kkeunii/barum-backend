from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    """
    사용자 생성 요청 DTO.
    """

    learner_code: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=50)
    age_group: Optional[str] = Field(default=None, max_length=50)
    native_language: Optional[str] = Field(default=None, max_length=50)
    korean_exposure_level: Optional[str] = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    """
    사용자 응답 DTO.
    """

    id: UUID
    learner_code: str
    display_name: Optional[str]
    age_group: Optional[str]
    native_language: Optional[str]
    korean_exposure_level: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
