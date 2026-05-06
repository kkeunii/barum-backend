from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.exceptions import (
    DuplicateLearnerCodeException,
    UserNotFoundException,
)
from app.domains.users.models import User
from app.domains.users.repository import UserRepository
from app.domains.users.schemas import UserCreateRequest


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

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundException()

        return user