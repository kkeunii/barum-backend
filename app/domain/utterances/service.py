from app.domain.utterances.exceptions import (
    LessonNotFoundException,
    SceneNotFoundException,
    UtteranceNotFoundException,
)
from app.domain.utterances.loader import (
    UtteranceMetadata,
    load_all_utterance_metadata,
    load_utterance_metadata,
)
from app.domain.utterances.schemas import (
    LessonResponse,
    SceneResponse,
    UtteranceResponse,
)


class UtteranceService:
    def get_lessons(self) -> list[LessonResponse]:
        utterances = load_all_utterance_metadata()
        lessons_by_id: dict[str, dict[str, object]] = {}
        for utterance in utterances:
            lesson_id = utterance.lesson_id or "default_lesson"
            lesson = lessons_by_id.setdefault(
                lesson_id,
                {
                    "lesson_id": lesson_id,
                    "title": utterance.lesson_name or lesson_id,
                    "lesson_name": utterance.lesson_name,
                    "difficulty": utterance.difficulty,
                    "scene_ids": [],
                },
            )
            scene_id = utterance.scene_id or "default_scene"
            if scene_id not in lesson["scene_ids"]:
                lesson["scene_ids"].append(scene_id)

        return [LessonResponse(**lesson) for lesson in lessons_by_id.values()]

    def get_lesson(self, lesson_id: str) -> LessonResponse:
        utterances = load_all_utterance_metadata()
        lesson_utterances = [
            utterance for utterance in utterances if utterance.lesson_id == lesson_id
        ]
        if not lesson_utterances:
            raise LessonNotFoundException()

        lesson = lesson_utterances[0]
        scene_ids = []
        for utterance in lesson_utterances:
            scene_id = utterance.scene_id or "default_scene"
            if scene_id not in scene_ids:
                scene_ids.append(scene_id)

        return LessonResponse(
            lesson_id=lesson.lesson_id,
            title=lesson.lesson_name or lesson.lesson_id,
            lesson_name=lesson.lesson_name,
            difficulty=lesson.difficulty,
            scene_ids=scene_ids,
        )

    def get_scene(self, scene_id: str) -> SceneResponse:
        utterances = load_all_utterance_metadata()
        scene_utterances = [
            utterance for utterance in utterances if utterance.scene_id == scene_id
        ]
        if not scene_utterances:
            raise SceneNotFoundException()

        sample = scene_utterances[0]
        return SceneResponse(
            scene_id=scene_id,
            scene_name=sample.scene_name,
            lesson_id=sample.lesson_id,
            lesson_name=sample.lesson_name,
            utterance_count=len(scene_utterances),
        )

    def get_scene_utterances(self, scene_id: str) -> list[UtteranceResponse]:
        utterances = load_all_utterance_metadata()
        scene_utterances = [
            utterance for utterance in utterances if utterance.scene_id == scene_id
        ]
        if not scene_utterances:
            raise SceneNotFoundException()

        return [self._to_utterance_response(utterance) for utterance in scene_utterances]

    def get_utterance(self, utterance_id: str) -> UtteranceResponse:
        metadata = load_utterance_metadata(utterance_id)
        return self._to_utterance_response(metadata)

    def _to_utterance_response(self, metadata: UtteranceMetadata) -> UtteranceResponse:
        return UtteranceResponse(
            utterance_id=metadata.utterance_id,
            lesson_id=metadata.lesson_id,
            lesson_name=metadata.lesson_name,
            scene_id=metadata.scene_id,
            scene_name=metadata.scene_name,
            clip_filename=metadata.clip_filename,
            clip_start_sec=metadata.clip_start_sec,
            clip_end_sec=metadata.clip_end_sec,
            pause_sec=metadata.pause_sec,
            subtitle_text=metadata.subtitle_text,
            practice_text=metadata.practice_text,
            normalized_text=metadata.normalized_text,
            target_phoneme_group=metadata.target_phoneme_group,
            target_prosody_type=metadata.target_prosody_type,
            difficulty=metadata.difficulty,
            memo=metadata.memo,
            reference_audio_path=metadata.reference_audio_path_raw,
        )
