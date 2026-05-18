from app.core.exception import AppException


class SceneNotFoundException(AppException):
    status_code = 404
    code = "SCENE_NOT_FOUND"
    message = "씬을 찾을 수 없습니다."
