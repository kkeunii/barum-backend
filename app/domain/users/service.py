from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attempts.storage import get_attempts_by_user, get_phoneme_analysis
from app.domain.users.exceptions import (
    DuplicateLearnerCodeException,
    UserNotFoundException,
)
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import (
    DailyLearningStatsResponse,
    RecentAttemptResponse,
    UserCreateRequest,
    UserStatsResponse,
    WeakPhonemeResponse,
)


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

    async def get_recent_attempts(self, user_id: int) -> list[RecentAttemptResponse]:
        await self.get_user(user_id)

        attempts = get_attempts_by_user(str(user_id))
        sorted_attempts = sorted(
            attempts,
            key=lambda attempt: attempt.get("updated_at", ""),
            reverse=True,
        )
        return [
            RecentAttemptResponse(
                attempt_id=str(attempt.get("attempt_id")),
                utterance_id=str(attempt.get("utterance_id")),
                status=str(attempt.get("status")),
                lesson_id=self._optional_str(attempt.get("lesson_id")),
                lesson_name=self._optional_str(attempt.get("lesson_name")),
                scene_id=self._optional_str(attempt.get("scene_id")),
                scene_name=self._optional_str(attempt.get("scene_name")),
                practice_text=self._optional_str(attempt.get("practice_text")),
                score=self._optional_float(attempt.get("score")),
                feedback_message=self._optional_str(
                    attempt.get("feedback_message"),
                ),
                created_at=self._parse_datetime(attempt.get("created_at")),
                updated_at=self._parse_datetime(attempt.get("updated_at")),
            )
            for attempt in sorted_attempts[:10]
        ]

    async def get_weak_phonemes(self, user_id: int) -> list[WeakPhonemeResponse]:
        await self.get_user(user_id)

        attempts = get_attempts_by_user(str(user_id))
        group_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {
                "matches": 0,
                "mismatches": 0,
                "attempt_count": 0,
            },
        )

        for attempt in attempts:
            if attempt.get("status") != "completed":
                continue

            attempt_id = attempt.get("attempt_id")
            if not attempt_id:
                continue

            phoneme_analysis = get_phoneme_analysis(str(attempt_id))
            if phoneme_analysis is not None:
                self._add_phoneme_analysis_stats(group_stats, phoneme_analysis)
                continue

            top_mismatch = attempt.get("top_mismatch")
            if isinstance(top_mismatch, dict):
                group = top_mismatch.get("target_group") or attempt.get(
                    "target_phoneme_group",
                )
                if group:
                    group_stats[str(group)]["mismatches"] += 1
                    group_stats[str(group)]["attempt_count"] += 1

        weak_phonemes = []
        for group, stats in group_stats.items():
            total = stats["matches"] + stats["mismatches"]
            accuracy = None
            if total:
                accuracy = round((stats["matches"] / total) * 100, 2)

            weak_phonemes.append(
                WeakPhonemeResponse(
                    phoneme_group=group,
                    matches=stats["matches"],
                    mismatches=stats["mismatches"],
                    total=total,
                    accuracy=accuracy,
                    attempt_count=stats["attempt_count"],
                ),
            )

        return sorted(
            weak_phonemes,
            key=lambda item: (
                item.accuracy if item.accuracy is not None else 100,
                -item.mismatches,
            ),
        )

    async def get_stats(self, user_id: int) -> UserStatsResponse:
        await self.get_user(user_id)

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
        return UserStatsResponse(
            user_id=user_id,
            total_attempts=len(attempts),
            completed_attempts=len(completed_attempts),
            average_score=average_score,
            daily_learning=self._build_daily_learning_stats(attempts),
        )

    def _build_daily_learning_stats(
        self,
        attempts: list[dict[str, Any]],
    ) -> list[DailyLearningStatsResponse]:
        daily_stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "total_attempts": 0,
                "completed_attempts": 0,
                "scores": [],
            },
        )

        for attempt in attempts:
            timestamp = attempt.get("updated_at") or attempt.get("created_at")
            date_key = self._parse_datetime(timestamp).date().isoformat()
            stats = daily_stats[date_key]
            stats["total_attempts"] += 1
            if attempt.get("status") == "completed":
                stats["completed_attempts"] += 1
                score = self._optional_float(attempt.get("score"))
                if score is not None:
                    stats["scores"].append(score)

        responses = []
        for date_key, stats in daily_stats.items():
            average_score = None
            if stats["scores"]:
                average_score = round(
                    sum(stats["scores"]) / len(stats["scores"]),
                    2,
                )
            responses.append(
                DailyLearningStatsResponse(
                    date=date_key,
                    total_attempts=stats["total_attempts"],
                    completed_attempts=stats["completed_attempts"],
                    average_score=average_score,
                ),
            )

        return sorted(responses, key=lambda item: item.date)

    def _add_phoneme_analysis_stats(
        self,
        group_stats: dict[str, dict[str, int]],
        phoneme_analysis: dict[str, Any],
    ) -> None:
        comparison = phoneme_analysis.get("comparison")
        if not isinstance(comparison, dict):
            return

        target_group_matches = comparison.get("target_group_matches")
        if not isinstance(target_group_matches, dict):
            return

        for group, result in target_group_matches.items():
            if not isinstance(result, dict):
                continue
            matches = int(result.get("matches", 0) or 0)
            mismatches = int(result.get("mismatches", 0) or 0)
            if matches == 0 and mismatches == 0:
                continue
            group_stats[str(group)]["matches"] += matches
            group_stats[str(group)]["mismatches"] += mismatches
            group_stats[str(group)]["attempt_count"] += 1

    def _parse_datetime(self, value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return datetime.now()

    def _optional_str(self, value: object) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    def _optional_float(self, value: object) -> Optional[float]:
        if value is None:
            return None
        return float(value)
