from pathlib import Path
from typing import Any, Dict

from app.domain.attempts.exceptions import (
    AttemptInvalidRequestException,
    AttemptNotFoundException,
    AttemptNotReadyException,
)
from app.domain.attempts.storage import (
    AttemptNotFoundError,
    create_attempt,
    get_attempt,
    get_phoneme_analysis,
    get_pitch_analysis,
    save_analysis_result,
    update_attempt,
)
from app.domain.utterances.loader import load_utterance_metadata, MetadataError


class AttemptService:
    def start_attempt(self, user_id: str, utterance_id: str) -> Dict[str, Any]:
        try:
            load_utterance_metadata(utterance_id)
        except MetadataError as exc:
            raise AttemptInvalidRequestException(str(exc))

        return create_attempt(user_id, utterance_id)

    def save_attempt_audio(
        self,
        attempt_id: str,
        audio_path: Path,
    ) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        update_attempt(
            attempt_id,
            {
                "status": "processing",
                "audio_path": str(audio_path),
                "error": None,
            },
        )

        try:
            from app.domain.attempts.analysis import run_full_analysis_from_metadata

            analysis_result = run_full_analysis_from_metadata(
                attempt["utterance_id"],
                audio_path,
            )
            return save_analysis_result(attempt_id, analysis_result)
        except MetadataError as exc:
            update_attempt(
                attempt_id,
                {
                    "status": "failed",
                    "error": str(exc),
                },
            )
            raise AttemptInvalidRequestException(str(exc))
        except Exception as exc:
            update_attempt(
                attempt_id,
                {
                    "status": "failed",
                    "error": f"analysis failed: {exc}",
                },
            )
            raise

    def get_attempt_status(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        return {
            "attempt_id": attempt["attempt_id"],
            "user_id": attempt["user_id"],
            "utterance_id": attempt["utterance_id"],
            "status": attempt["status"],
            "created_at": attempt["created_at"],
            "updated_at": attempt["updated_at"],
            "error": attempt.get("error"),
        }

    def get_attempt_result(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        return {
            "attempt_id": attempt["attempt_id"],
            "user_id": attempt["user_id"],
            "utterance_id": attempt["utterance_id"],
            "status": attempt["status"],
            "score": attempt.get("score"),
            "feedback_type": attempt.get("feedback_type"),
            "feedback_message": attempt.get("feedback_message"),
            "clip_filename": attempt.get("clip_filename"),
            "clip_start_sec": attempt.get("clip_start_sec"),
            "clip_end_sec": attempt.get("clip_end_sec"),
            "pause_sec": attempt.get("pause_sec"),
            "subtitle_text": attempt.get("subtitle_text"),
            "practice_text": attempt.get("practice_text"),
            "normalized_text": attempt.get("normalized_text"),
            "difficulty": attempt.get("difficulty"),
            "lesson_id": attempt.get("lesson_id"),
            "lesson_name": attempt.get("lesson_name"),
            "scene_id": attempt.get("scene_id"),
            "scene_name": attempt.get("scene_name"),
            "target_phoneme_group": attempt.get("target_phoneme_group"),
            "target_phoneme_group_raw": attempt.get("target_phoneme_group_raw"),
            "target_prosody_type": attempt.get("target_prosody_type"),
            "error": attempt.get("error"),
        }

    def retry_attempt(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        if attempt["status"] == "completed":
            raise AttemptInvalidRequestException("completed attempts cannot be retried")

        update_attempt(
            attempt_id,
            {
                "status": "started",
                "error": None,
                "score": None,
                "feedback_type": None,
                "feedback_message": None,
            },
        )
        return self._load_attempt(attempt_id)

    def get_phoneme_analysis(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        self._raise_if_not_ready(attempt)
        analysis = get_phoneme_analysis(attempt_id)
        if analysis is None:
            raise AttemptNotFoundException("phoneme analysis not found")
        return analysis

    def get_pitch_analysis(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        self._raise_if_not_ready(attempt)
        analysis = get_pitch_analysis(attempt_id)
        if analysis is None:
            raise AttemptNotFoundException("pitch analysis not found")
        return analysis

    def get_feedback(self, attempt_id: str) -> Dict[str, Any]:
        attempt = self._load_attempt(attempt_id)
        self._raise_if_not_ready(attempt)
        return {
            "attempt_id": attempt["attempt_id"],
            "feedback_type": attempt.get("feedback_type"),
            "feedback_message": attempt.get("feedback_message"),
            "top_mismatch": attempt.get("top_mismatch"),
            "score": attempt.get("score"),
        }

    def _load_attempt(self, attempt_id: str) -> Dict[str, Any]:
        try:
            return get_attempt(attempt_id)
        except AttemptNotFoundError as exc:
            raise AttemptNotFoundException(str(exc))

    def _raise_if_not_ready(self, attempt: Dict[str, Any]) -> None:
        if attempt["status"] != "completed":
            raise AttemptNotReadyException()
