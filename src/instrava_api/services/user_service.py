from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from instrava_api.core.exceptions import EmailAlreadyRegisteredError
from instrava_api.core.security import get_password_hash
from instrava_api.models.user import User
from instrava_api.repositories.user_repository import UserRepository
from instrava_api.schemas.user import UserRegister


class UserService:
    def __init__(
        self, session: AsyncSession, user_repo: UserRepository | None = None
    ) -> None:
        self.session = session
        self.user_repo = user_repo or UserRepository(session)

    async def register_user(self, user_in: UserRegister) -> User:
        """Register a new user after validating uniqueness and hashing password."""
        normalized_email = user_in.email.strip().lower()

        existing_user = await self.user_repo.get_by_email(normalized_email)
        if existing_user is not None:
            raise EmailAlreadyRegisteredError()

        password_hash = get_password_hash(user_in.password)

        new_user = User(
            name=user_in.name.strip(),
            email=normalized_email,
            password_hash=password_hash,
        )

        try:
            user = await self.user_repo.create(new_user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as exc:
            await self.session.rollback()
            # Handle potential race conditions with unique constraints
            raise EmailAlreadyRegisteredError() from exc
