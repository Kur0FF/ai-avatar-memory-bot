from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Message


async def save(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
    role: str,
    content: str,
) -> None:
    session.add(
        Message(user_id=user_id, avatar_id=avatar_id, role=role, content=content)
    )
    await session.commit()


async def get_last_n(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
    limit: int = 10,
) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.user_id == user_id, Message.avatar_id == avatar_id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    # Fetch DESC for efficiency, then reverse to get chronological order
    return list(reversed(result.scalars().all()))


async def count_user_messages(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
) -> int:
    """Return total number of user-role messages for this (user, avatar) pair."""
    result = await session.execute(
        select(func.count()).where(
            Message.user_id == user_id,
            Message.avatar_id == avatar_id,
            Message.role == "user",
        )
    )
    return result.scalar_one()


async def delete_history(
    session: AsyncSession, user_id: int, avatar_id: int
) -> None:
    await session.execute(
        delete(Message).where(
            Message.user_id == user_id, Message.avatar_id == avatar_id
        )
    )
    await session.commit()
