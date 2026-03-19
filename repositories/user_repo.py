from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def get_or_create(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(user_id=user_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def set_avatar(session: AsyncSession, user_id: int, avatar_id: int) -> None:
    user = await get_or_create(session, user_id)
    user.current_avatar_id = avatar_id
    await session.commit()


async def get_current_avatar_id(session: AsyncSession, user_id: int) -> int | None:
    result = await session.execute(
        select(User.current_avatar_id).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()
