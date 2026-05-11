from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attempts.storage import get_attempts_by_user
from app.domain.users.exceptions import (
    DuplicateLearnerCodeException,
    UserNotFoundException,
)
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserCreateRequest


class UserService:
    """
    사용자 Service.
    비즈니스 로직을 담당한다.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def create_user(self, payload: UserCreateRequest) -> User:
        existing_user = await self.user_repository.get_by_learner_code(
            payload.learner_code,
        )

        if existing_user is not None:
            raise DuplicateLearnerCodeException()

        user = User(
            learner_code=payload.learner_code,
            display_name=payload.display_name,
            age_group=payload.age_group,
            native_language=payload.native_language,
            korean_exposure_level=payload.korean_exposure_level,
        )

        saved_user = await self.user_repository.save(user)

        await self.db.commit()
        await self.db.refresh(saved_user)

        return saved_user

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundException()

        return user

    async def get_recent_attempts(self, user_id: int) -> list[dict[str, object]]:
        attempts = get_attempts_by_user(str(user_id))
        sorted_attempts = sorted(
            attempts,
            key=lambda attempt: attempt.get("updated_at", ""),
            reverse=True,
        )
        return sorted_attempts[:10]

    async def get_weak_phonemes(self, user_id: int) -> dict[str, int]:
        attempts = get_attempts_by_user(str(user_id))
        counts: dict[str, int] = {}
        for attempt in attempts:
            top_mismatch = attempt.get("top_mismatch")
            if isinstance(top_mismatch, dict):
                group = top_mismatch.get("target_group") or attempt.get("target_phoneme_group")
                if group:
                    counts[group] = counts.get(group, 0) + 1
        return counts

    async def get_stats(self, user_id: int) -> dict[str, object]:
        attempts = get_attempts_by_user(str(user_id))
        completed_attempts = [
            attempt for attempt in attempts if attempt.get("status") == "completed"
        ]
        average_score = None
        if completed_attempts:
            average_score = round(
                sum(
                    float(attempt.get("score", 0) or 0)
                    for attempt in completed_attempts
                )
                / len(completed_attempts),
                2,
            )
        return {
            "user_id": user_id,
            "total_attempts": len(attempts),
            "completed_attempts": len(completed_attempts),
            "average_score": average_score,
            "weak_phoneme_groups": await self.get_weak_phonemes(user_id),
        }
