from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class LessonResponse(BaseModel):
    lesson_id: str
    lesson_name: str
    title: str
    difficulty: str
    scene_ids: list[str]

    model_config = ConfigDict(from_attributes=True)


class SceneResponse(BaseModel):
    scene_id: str
    scene_name: str
    lesson_id: str
    lesson_name: str
    utterance_count: int

    model_config = ConfigDict(from_attributes=True)


class UtteranceResponse(BaseModel):
    utterance_id: str
    lesson_id: str
    lesson_name: str
    scene_id: str
    scene_name: str
    clip_filename: str
    clip_start_sec: float
    clip_end_sec: float
    pause_sec: float
    subtitle_text: str
    practice_text: str
    normalized_text: str
    target_phoneme_group: str
    target_prosody_type: str
    difficulty: str
    memo: str
    reference_audio_path: str

    model_config = ConfigDict(from_attributes=True)
