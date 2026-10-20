from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from instrava_api.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email (case-insensitive match on normalized email)."""
        normalized_email = email.strip().lower()
        stmt = select(User).where(User.email == normalized_email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        """Add and flush a user to the database."""
        self.session.add(user)
        await self.session.flush()
        return user
