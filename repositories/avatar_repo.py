from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Avatar


async def get_all(session: AsyncSession) -> list[Avatar]:
    result = await session.execute(select(Avatar).order_by(Avatar.id))
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, avatar_id: int) -> Avatar | None:
    result = await session.execute(select(Avatar).where(Avatar.id == avatar_id))
    return result.scalar_one_or_none()
