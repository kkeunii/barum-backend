from app.core.exception import AppException


class UtteranceNotFoundException(AppException):
    status_code = 404
    code = "UTTERANCE_NOT_FOUND"
    message = "요청한 발화 문장을 찾을 수 없습니다."


class LessonNotFoundException(AppException):
    status_code = 404
    code = "LESSON_NOT_FOUND"
    message = "요청한 레슨을 찾을 수 없습니다."


class SceneNotFoundException(AppException):
    status_code = 404
    code = "SCENE_NOT_FOUND"
    message = "요청한 장면을 찾을 수 없습니다."
