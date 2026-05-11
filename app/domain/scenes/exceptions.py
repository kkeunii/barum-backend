from app.core.exception import AppException


class SceneNotFoundException(AppException):
    status_code = 404
    code = "SCENE_NOT_FOUND"
    message = "해당 scene_id를 찾을 수 없습니다."
