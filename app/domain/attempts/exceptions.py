from app.core.exception import AppException


class AttemptNotFoundException(AppException):
    status_code = 404
    code = "ATTEMPT_NOT_FOUND"
    message = "요청한 시도 기록을 찾을 수 없습니다."


class AttemptNotReadyException(AppException):
    status_code = 409
    code = "ATTEMPT_NOT_READY"
    message = "분석이 아직 완료되지 않았습니다."


class AttemptInvalidRequestException(AppException):
    status_code = 400
    code = "ATTEMPT_INVALID_REQUEST"
    message = "잘못된 시도 요청입니다."
