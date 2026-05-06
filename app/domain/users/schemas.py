from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    """
    사용자 생성 요청 DTO.
    """

    learner_code: str = Field(..., min_length=1, max_length=100)
    display_name: str | None = Field(default=None, max_length=50)
    age_group: str | None = Field(default=None, max_length=50)
    native_language: str | None = Field(default=None, max_length=50)
    korean_exposure_level: str | None = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    """
    사용자 응답 DTO.
    """

    id: UUID
    learner_code: str
    display_name: str | None
    age_group: str | None
    native_language: str | None
    korean_exposure_level: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)