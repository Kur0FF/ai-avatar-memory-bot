import json
import logging
import re
import time
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest
from openai import AsyncOpenAI

from config import settings

if TYPE_CHECKING:
    from aiogram.types import Message as TgMessage

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=60.0,
        )
    return _client


UPDATE_INTERVAL = 0.7   # seconds between Telegram message edits
MIN_NEW_CHARS = 30      # minimum new characters before forced update


async def stream_chat(
    tg_message: "TgMessage",
    prompt_messages: list[dict[str, str]],
) -> str:
    """
    Stream LLM response and update Telegram message with buffered edits.
    Returns the full response text, or "" on LLM failure.
    """
    placeholder = await tg_message.answer("Думаю\u2026")
    full_text = ""
    last_edit_len = 0
    last_update_at = time.monotonic()

    try:
        stream = await get_client().chat.completions.create(
            model=settings.llm_model,
            messages=prompt_messages,  # type: ignore[arg-type]
            stream=True,
            temperature=0.8,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_text += delta

            now = time.monotonic()
            new_chars = len(full_text) - last_edit_len
            time_elapsed = now - last_update_at

            if full_text.strip() and (
                time_elapsed >= UPDATE_INTERVAL or new_chars >= MIN_NEW_CHARS
            ):
                try:
                    await placeholder.edit_text(full_text)
                    last_edit_len = len(full_text)
                    last_update_at = now
                except TelegramBadRequest:
                    # MessageNotModified or similar — still update counters
                    last_edit_len = len(full_text)
                    last_update_at = now
                except Exception:
                    pass  # RetryAfter, network — skip this update, try next time

        # Final edit — always show complete text
        if full_text.strip():
            try:
                await placeholder.edit_text(full_text)
            except TelegramBadRequest as e:
                # MessageNotModified: text already up to date — that's fine
                if "message is not modified" not in str(e).lower():
                    # Some other bad request (e.g. message deleted) — send as new
                    await tg_message.answer(full_text)
            except Exception:
                await tg_message.answer(full_text)
        else:
            try:
                await placeholder.edit_text("(пустой ответ от ИИ)")
            except Exception:
                pass

    except Exception as exc:
        logger.warning("LLM stream error: %s", exc)
        try:
            await placeholder.edit_text(
                "Извините, ИИ перегружен, попробуйте позже."
            )
        except Exception:
            await tg_message.answer(
                "Извините, ИИ перегружен, попробуйте позже."
            )
        return ""

    return full_text


# ── Fact extraction ────────────────────────────────────────────────────────────

_FACT_EXTRACTION_SYSTEM = (
    "You are a memory extraction assistant. "
    "Analyze the dialogue and extract durable facts about the user "
    "(name, age, profession, interests, life events, preferences, goals). "
    "Return ONLY a valid JSON array of strings, nothing else. "
    'Example: ["User\'s name is Alex", "User likes Python", "User has a cat"]\n'
    "If no facts found, return: []"
)


async def extract_facts(messages: list[dict[str, str]]) -> list[str]:
    """Call LLM to extract durable facts from dialogue. Never raises."""
    dialogue = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    try:
        response = await get_client().chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": _FACT_EXTRACTION_SYSTEM},
                {
                    "role": "user",
                    "content": f"Extract facts from this dialogue:\n\n{dialogue}",
                },
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content or ""
        return _parse_facts_json(raw)
    except Exception:
        return []


def _parse_facts_json(raw: str) -> list[str]:
    """
    Three-level robust JSON parsing:
    1. Direct json.loads
    2. Regex extraction of [...] fragment
    3. Line-by-line fallback
    """
    raw = raw.strip()

    # Attempt 1: direct parse
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(f).strip() for f in parsed if str(f).strip()]
    except (json.JSONDecodeError, ValueError):
        pass

    # Attempt 2: extract JSON array from surrounding text
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return [str(f).strip() for f in parsed if str(f).strip()]
        except (json.JSONDecodeError, ValueError):
            pass

    # Attempt 3: line-by-line fallback (LLM returned a bullet list)
    lines: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line in ("[", "]", "{", "}"):
            continue
        # Strip leading bullet/number markers
        line = re.sub(r"^[\-\*•\d\.]+\s*", "", line).strip('" ,')
        if line:
            lines.append(line)

    return lines
