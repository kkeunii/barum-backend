from __future__ import annotations

from datetime import datetime
from typing import Optional

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

    user_id: int
    learner_code: str
    display_name: Optional[str]
    age_group: Optional[str]
    native_language: Optional[str]
    korean_exposure_level: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecentAttemptResponse(BaseModel):
    """
    최근 학습 기록 응답 DTO.
    """

    attempt_id: str
    utterance_id: str
    status: str
    lesson_id: Optional[str]
    lesson_name: Optional[str]
    scene_id: Optional[str]
    scene_name: Optional[str]
    practice_text: Optional[str]
    score: Optional[float]
    feedback_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class WeakPhonemeResponse(BaseModel):
    """
    취약 음소 그룹 응답 DTO.
    """

    phoneme_group: str
    matches: int
    mismatches: int
    total: int
    accuracy: Optional[float]
    attempt_count: int


class DailyLearningStatsResponse(BaseModel):
    """
    날짜별 학습량 응답 DTO.
    """

    date: str
    total_attempts: int
    completed_attempts: int
    average_score: Optional[float]


class UserStatsResponse(BaseModel):
    """
    사용자 학습 통계 응답 DTO.
    """

    user_id: int
    total_attempts: int
    completed_attempts: int
    average_score: Optional[float]
    daily_learning: list[DailyLearningStatsResponse]
