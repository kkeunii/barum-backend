from app.core.exceptions import AppException


class UserNotFoundException(AppException):
    status_code = 404
    code = "USER_NOT_FOUND"
    message = "사용자를 찾을 수 없습니다."


class DuplicateLearnerCodeException(AppException):
    status_code = 409
    code = "DUPLICATE_LEARNER_CODE"
    message = "이미 존재하는 learner_code입니다."