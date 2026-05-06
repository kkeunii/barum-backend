from __future__ import annotations

from typing import Optional


class AppException(Exception):
    """
    프로젝트 공통 예외 베이스.
    """

    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"
    message: str = "서버 내부 오류가 발생했습니다."

    def __init__(self, message: Optional[str] = None):
        if message is not None:
            self.message = message
