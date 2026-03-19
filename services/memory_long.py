import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import fact_repo
from services import llm

logger = logging.getLogger(__name__)

EXTRACTION_EVERY_N = 4  # extract facts every N user messages


async def get_facts_block(
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
) -> str | None:
    """Return a formatted facts block for the system prompt, or None."""
    facts = await fact_repo.get_all(session, user_id, avatar_id)
    if not facts:
        return None
    lines = "\n".join(f"- {f.fact_text}" for f in facts)
    return f"Важно: ты помнишь об этом пользователе следующее:\n{lines}"


async def maybe_extract_and_save_facts(
    user_id: int,
    avatar_id: int,
    recent_messages: list[dict[str, str]],
) -> None:
    """
    Check if it's time to extract facts (every EXTRACTION_EVERY_N user messages).
    Schedules extraction as a background task with its own DB session.
    The caller's session is NOT passed — it will be closed by the time the task runs.
    """
    user_msg_count = sum(1 for m in recent_messages if m["role"] == "user")
    if user_msg_count > 0 and user_msg_count % EXTRACTION_EVERY_N == 0:
        asyncio.create_task(
            _extract_and_save(user_id, avatar_id, list(recent_messages))
        )


async def _extract_and_save(
    user_id: int,
    avatar_id: int,
    messages: list[dict[str, str]],
) -> None:
    """
    Background task: extract facts and persist them.
    Opens its own DB session — safe to run after the handler's session is closed.
    """
    from database.engine import async_session_factory  # local import avoids circular

    try:
        new_facts = await llm.extract_facts(messages)
        if not new_facts:
            return
        async with async_session_factory() as session:
            await fact_repo.save_new_facts(session, user_id, avatar_id, new_facts)
            logger.info(
                "Saved %d new facts for user=%s avatar=%s",
                len(new_facts), user_id, avatar_id,
            )
    except Exception as exc:
        logger.warning("Background fact extraction failed: %s", exc)
