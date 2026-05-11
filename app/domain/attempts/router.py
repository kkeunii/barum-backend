from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.domain.attempts.dependencies import get_attempt_service
from app.domain.attempts.exceptions import (
    AttemptInvalidRequestException,
    AttemptNotFoundException,
    AttemptNotReadyException,
)
from app.domain.attempts.schemas import (
    AttemptFeedbackResponse,
    AttemptResultResponse,
    AttemptStatusResponse,
    StartAttemptRequest,
)
from app.domain.attempts.service import AttemptService

router = APIRouter(tags=["attempts"])


def _to_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, AttemptNotFoundException):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, AttemptNotReadyException):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, AttemptInvalidRequestException):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/start",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def start_attempt(
    payload: StartAttemptRequest,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.start_attempt(payload.user_id, payload.utterance_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.post("/{attempt_id}/audio")
async def upload_attempt_audio(
    attempt_id: str,
    audio_file: UploadFile = File(...),
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    audio_dir = Path("data") / "audio" / "attempts" / attempt_id / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    uploaded_filename = Path(audio_file.filename or "uploaded_audio").name
    audio_path = audio_dir / uploaded_filename
    audio_path.write_bytes(await audio_file.read())

    try:
        return attempt_service.save_attempt_audio(attempt_id, audio_path)
    except Exception as exc:
        raise _to_http_error(exc)


@router.get("/{attempt_id}/status", response_model=AttemptStatusResponse)
def get_attempt_status(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.get_attempt_status(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.get("/{attempt_id}/result", response_model=AttemptResultResponse)
def get_attempt_result(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.get_attempt_result(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.post("/{attempt_id}/retry", response_model=Dict[str, Any])
def retry_attempt(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.retry_attempt(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.get("/{attempt_id}/phoneme")
def get_attempt_phoneme(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.get_phoneme_analysis(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.get("/{attempt_id}/pitch")
def get_attempt_pitch(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.get_pitch_analysis(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)


@router.get("/{attempt_id}/feedback", response_model=AttemptFeedbackResponse)
def get_attempt_feedback(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> Dict[str, Any]:
    try:
        return attempt_service.get_feedback(attempt_id)
    except Exception as exc:
        raise _to_http_error(exc)
