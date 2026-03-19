from sqlalchemy.ext.asyncio import AsyncSession

from repositories import message_repo

HISTORY_LIMIT = 10


async def get_context(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
) -> list[dict[str, str]]:
    """
    Return the last HISTORY_LIMIT messages as OpenAI-compatible dicts,
    in chronological order (oldest → newest).
    """
    messages = await message_repo.get_last_n(
        session, user_id, avatar_id, limit=HISTORY_LIMIT
    )
    return [{"role": m.role, "content": m.content} for m in messages]
