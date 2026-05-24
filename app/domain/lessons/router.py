from fastapi import APIRouter, Depends

from app.domain.lessons.dependencies import get_lesson_service
from app.domain.lessons.schemas import LessonDetailResponse, LessonResponse
from app.domain.lessons.service import LessonService

router = APIRouter()


@router.get(
    "",
    response_model=list[LessonResponse],
)
async def get_lessons(
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    레슨 목록 조회 API.
    """

    return await lesson_service.get_lessons()


@router.get(
    "/{lesson_id}",
    response_model=LessonDetailResponse,
)
async def get_lesson(
    lesson_id: int,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    레슨 상세 조회 API.
    """

    return await lesson_service.get_lesson(lesson_id)
