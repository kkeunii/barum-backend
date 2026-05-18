from fastapi import APIRouter, Depends, status

from app.domain.users.dependencies import get_user_service
from app.domain.users.schemas import (
    RecentAttemptResponse,
    UserCreateRequest,
    UserResponse,
    UserStatsResponse,
    WeakPhonemeResponse,
)
from app.domain.users.service import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 생성 API.
    """

    return await user_service.create_user(payload)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 단건 조회 API.
    """

    return await user_service.get_user(user_id)


@router.get(
    "/{user_id}/attempts/recent",
    response_model=list[RecentAttemptResponse],
)
async def get_recent_attempts(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 최근 학습 기록 조회 API.
    """

    return await user_service.get_recent_attempts(user_id)


@router.get(
    "/{user_id}/weak-phonemes",
    response_model=list[WeakPhonemeResponse],
)
async def get_weak_phonemes(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 취약 음소 요약 조회 API.
    """

    return await user_service.get_weak_phonemes(user_id)


@router.get(
    "/{user_id}/stats",
    response_model=UserStatsResponse,
)
async def get_user_stats(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 학습 통계 조회 API.
    """

    return await user_service.get_stats(user_id)
