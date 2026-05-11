from fastapi import Depends
from app.domain.utterances.service import UtteranceService


def get_utterance_service() -> UtteranceService:
    return UtteranceService()
