from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from fsm.states import BotStates
from keyboards.avatar_keyboard import build_avatar_keyboard
from repositories import avatar_repo, fact_repo, message_repo, user_repo

router = Router()


async def _get_avatar_id(state: FSMContext, session: AsyncSession, user_id: int) -> int | None:
    data = await state.get_data()
    avatar_id: int | None = data.get("avatar_id")
    if avatar_id is None:
        avatar_id = await user_repo.get_current_avatar_id(session, user_id)
        if avatar_id is not None:
            await state.update_data(avatar_id=avatar_id)
    return avatar_id


@router.message(Command("history"))
async def cmd_history(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    avatar_id = await _get_avatar_id(state, session, message.from_user.id)
    if avatar_id is None:
        await message.answer("Сначала выберите аватара: /start")
        return

    messages = await message_repo.get_last_n(
        session, message.from_user.id, avatar_id, limit=10
    )

    if not messages:
        await message.answer("История диалога пуста.")
        return

    lines = []
    for m in messages:
        role_label = "\U0001f464 Вы" if m.role == "user" else "\U0001f916 ИИ"
        preview = m.content[:200] + ("…" if len(m.content) > 200 else "")
        lines.append(f"<b>{role_label}:</b> {preview}")

    await message.answer(
        "\U0001f4dc <b>Последние сообщения:</b>\n\n" + "\n\n".join(lines),
        parse_mode="HTML",
    )


@router.message(Command("facts"))
async def cmd_facts(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    avatar_id = await _get_avatar_id(state, session, message.from_user.id)
    if avatar_id is None:
        await message.answer("Сначала выберите аватара: /start")
        return

    facts = await fact_repo.get_all(session, message.from_user.id, avatar_id)

    if not facts:
        await message.answer(
            "\U0001f9e0 Долгосрочная память пуста.\n"
            "Продолжайте разговор — бот запомнит важные факты о вас!"
        )
        return

    lines = [f"{i}. {f.fact_text}" for i, f in enumerate(facts, 1)]
    await message.answer(
        "\U0001f9e0 <b>Что я о вас помню:</b>\n\n" + "\n".join(lines),
        parse_mode="HTML",
    )


@router.message(Command("reset"))
async def cmd_reset(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    avatar_id = await _get_avatar_id(state, session, message.from_user.id)
    if avatar_id is None:
        await message.answer("Сначала выберите аватара: /start")
        return

    await message_repo.delete_history(session, message.from_user.id, avatar_id)
    await message.answer(
        "\U0001f504 <b>История диалога очищена.</b>\n"
        "Долгосрочная память сохранена — я всё ещё помню важные факты о вас!\n"
        "Используйте /facts чтобы проверить.",
        parse_mode="HTML",
    )


@router.message(Command("change_avatar"))
async def cmd_change_avatar(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    avatars = await avatar_repo.get_all(session)
    keyboard = build_avatar_keyboard(avatars)
    # Clear avatar_id from FSMContext so DB becomes sole source of truth after new selection
    await state.set_state(BotStates.choosing_avatar)
    await state.update_data(avatar_id=None)
    await message.answer(
        "\U0001f504 Выберите нового собеседника:",
        reply_markup=keyboard,
    )


