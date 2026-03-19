from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MemoryFact


async def get_all(
    session: AsyncSession, user_id: int, avatar_id: int
) -> list[MemoryFact]:
    result = await session.execute(
        select(MemoryFact)
        .where(MemoryFact.user_id == user_id, MemoryFact.avatar_id == avatar_id)
        .order_by(MemoryFact.created_at)
    )
    return list(result.scalars().all())


async def save_new_facts(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
    facts: list[str],
) -> None:
    existing = await get_all(session, user_id, avatar_id)
    existing_texts = {f.fact_text.lower().strip() for f in existing}

    for fact in facts:
        normalized = fact.strip()
        if not normalized:
            continue
        if normalized.lower() not in existing_texts:
            session.add(
                MemoryFact(
                    user_id=user_id,
                    avatar_id=avatar_id,
                    fact_text=normalized,
                )
            )
            existing_texts.add(normalized.lower())

    await session.commit()
