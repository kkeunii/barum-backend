from app.core.exception import AppException


class LessonNotFoundException(AppException):
    status_code = 404
    code = "LESSON_NOT_FOUND"
    message = "레슨을 찾을 수 없습니다."
