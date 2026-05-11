from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StartAttemptRequest(BaseModel):
    user_id: str
    utterance_id: str


class AttemptStatusResponse(BaseModel):
    attempt_id: str
    user_id: str
    utterance_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AttemptResultResponse(BaseModel):
    attempt_id: str
    user_id: str
    utterance_id: str
    status: str
    score: Optional[float]
    feedback_type: Optional[str]
    feedback_message: Optional[str]
    clip_filename: Optional[str]
    clip_start_sec: Optional[float]
    clip_end_sec: Optional[float]
    pause_sec: Optional[float]
    subtitle_text: Optional[str]
    practice_text: Optional[str]
    normalized_text: Optional[str]
    difficulty: Optional[str]
    lesson_id: Optional[str]
    lesson_name: Optional[str]
    scene_id: Optional[str]
    scene_name: Optional[str]
    target_phoneme_group: Optional[str]
    target_phoneme_group_raw: Optional[str]
    target_prosody_type: Optional[str]
    error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AttemptFeedbackResponse(BaseModel):
    attempt_id: str
    feedback_type: Optional[str]
    feedback_message: Optional[str]
    top_mismatch: Optional[dict[str, object]]
    score: Optional[float]

    model_config = ConfigDict(from_attributes=True)
