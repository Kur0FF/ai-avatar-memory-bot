from sqlalchemy.ext.asyncio import AsyncSession

from avatars.data import AVATARS
from database.engine import async_session_factory, enable_wal, engine
from database.models import Avatar, Base


async def create_tables_and_seed() -> None:
    """Create all tables and seed avatars if not present."""
    await enable_wal()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await _seed_avatars(session)


async def _seed_avatars(session: AsyncSession) -> None:
    from sqlalchemy import select

    result = await session.execute(select(Avatar))
    existing = result.scalars().all()

    if existing:
        return

    for avatar_data in AVATARS:
        session.add(
            Avatar(
                name=avatar_data.name,
                description=avatar_data.description,
                system_prompt=avatar_data.system_prompt,
            )
        )

    await session.commit()
