from app.domain.lessons.service import LessonService


def get_lesson_service() -> LessonService:
    return LessonService()
