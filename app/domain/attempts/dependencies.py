from fastapi import Depends

from app.domain.attempts.service import AttemptService


def get_attempt_service() -> AttemptService:
    return AttemptService()
