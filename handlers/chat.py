from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from fsm.states import BotStates
from repositories import avatar_repo, message_repo, user_repo
from services import llm, memory_long, memory_short, prompt_builder

router = Router()


@router.message(BotStates.chatting, F.text)
async def handle_chat_message(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    # Resolve avatar_id from FSM context or DB
    data = await state.get_data()
    avatar_id: int | None = data.get("avatar_id")
    if avatar_id is None:
        avatar_id = await user_repo.get_current_avatar_id(session, message.from_user.id)
        if avatar_id is None:
            await message.answer("Пожалуйста, выберите аватара: /start")
            return
        await state.update_data(avatar_id=avatar_id)

    avatar = await avatar_repo.get_by_id(session, avatar_id)
    if avatar is None:
        await message.answer("Аватар не найден. Выберите снова: /start")
        return

    # Save user message
    await message_repo.save(
        session, message.from_user.id, avatar_id, role="user", content=message.text
    )

    # Build prompt and stream response
    prompt = await prompt_builder.build_prompt(
        session, message.from_user.id, avatar, message.text
    )
    full_response = await llm.stream_chat(message, prompt)

    # Save assistant response
    if full_response:
        await message_repo.save(
            session,
            message.from_user.id,
            avatar_id,
            role="assistant",
            content=full_response,
        )

    # Trigger background fact extraction if needed (no session passed — task opens its own)
    recent = await memory_short.get_context(session, message.from_user.id, avatar_id)
    await memory_long.maybe_extract_and_save_facts(
        message.from_user.id, avatar_id, recent
    )


@router.message(F.text)
async def fallback_no_avatar(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    """
    Catches text messages when FSM state is empty (e.g. after bot restart).
    If the user already has a selected avatar in DB — restore the session silently
    and continue the dialogue. Otherwise prompt to /start.
    """
    avatar_id = await user_repo.get_current_avatar_id(session, message.from_user.id)
    if avatar_id is None:
        await message.answer(
            "Пожалуйста, выберите аватара для начала разговора: /start"
        )
        return

    # Restore FSM state from DB — transparent to the user
    await state.set_state(BotStates.chatting)
    await state.update_data(avatar_id=avatar_id)

    # Delegate to the main chat handler
    await handle_chat_message(message, state, session)
