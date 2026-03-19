from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Avatar
from services import memory_long, memory_short


async def build_prompt(
    session: AsyncSession,
    user_id: int,
    avatar: Avatar,
    new_user_message: str,
) -> list[dict[str, str]]:
    """
    Build the full prompt for the LLM.

    Order:
    1. system: avatar system_prompt + long-term facts (if any)
    2. messages: short-term history (last 10)
    3. user: the new message
    """
    # 1. System block — avatar character + long-term memory
    system_content = avatar.system_prompt
    facts_block = await memory_long.get_facts_block(session, user_id, avatar.id)
    if facts_block:
        system_content += f"\n\n{facts_block}"

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_content}
    ]

    # 2. Short-term history
    history = await memory_short.get_context(session, user_id, avatar.id)
    messages.extend(history)

    # 3. New user message
    messages.append({"role": "user", "content": new_user_message})

    return messages
