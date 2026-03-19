import asyncio
import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import fact_repo, message_repo
from services import llm

logger = logging.getLogger(__name__)

EXTRACTION_EVERY_N = 2   # trigger every N total user messages in DB
EXTRACTION_WINDOW = 30   # how many recent messages to pass to LLM for extraction

# Patterns that indicate an immediate personal disclosure.
# Extraction fires right away without waiting for the periodic counter.
_FACT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"меня зовут",
        r"мне \d+",
        r"\d+ лет",
        r"я люблю",
        r"я работаю",
        r"я хочу",
        r"мой\b",
        r"моя\b",
        r"моё\b",
        r"мои\b",
        r"я живу",
        r"я учусь",
        r"я занимаюсь",
        r"у меня есть",
        r"меня интересует",
    ]
]


def _contains_personal_fact(text: str) -> bool:
    return any(p.search(text) for p in _FACT_PATTERNS)


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
    session: AsyncSession,
    user_id: int,
    avatar_id: int,
    last_user_text: str,
) -> None:
    """
    Decide whether to schedule background fact extraction.

    Trigger logic:
      1. Periodic: total user message count in DB is divisible by EXTRACTION_EVERY_N.
      2. Immediate: the just-sent message matches a personal-fact pattern.

    Uses real DB count — not a sliding window — so the trigger is stable
    regardless of how long the conversation is.
    Background task opens its own DB session (caller's session may close first).
    """
    total = await message_repo.count_user_messages(session, user_id, avatar_id)
    if total == 0:
        return

    periodic = total % EXTRACTION_EVERY_N == 0
    immediate = _contains_personal_fact(last_user_text)

    if periodic or immediate:
        asyncio.create_task(
            _extract_and_save(user_id, avatar_id)
        )


async def _extract_and_save(user_id: int, avatar_id: int) -> None:
    """
    Background task: fetch the extraction window from DB, extract facts, persist.
    Opens its own DB session — safe to run after the handler's session is closed.
    """
    from database.engine import async_session_factory  # local import avoids circular

    try:
        async with async_session_factory() as session:
            rows = await message_repo.get_last_n(
                session, user_id, avatar_id, limit=EXTRACTION_WINDOW
            )
            messages = [{"role": m.role, "content": m.content} for m in rows]

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
