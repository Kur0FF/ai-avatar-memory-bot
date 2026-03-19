from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from fsm.states import BotStates
from keyboards.avatar_keyboard import build_avatar_keyboard
from repositories import avatar_repo, user_repo

router = Router()

_WELCOME_TEXT = (
    "\U0001f916 <b>Добро пожаловать в мир ИИ-аватаров!</b>\n\n"
    "Выберите собеседника, с которым хотите поговорить:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await user_repo.get_or_create(session, message.from_user.id)
    avatars = await avatar_repo.get_all(session)
    keyboard = build_avatar_keyboard(avatars)
    await state.set_state(BotStates.choosing_avatar)
    await state.update_data(avatar_id=None)  # clear stale avatar_id from FSMContext
    await message.answer(_WELCOME_TEXT, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("avatar:"), BotStates.choosing_avatar)
async def avatar_selected(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    avatar_id = int(callback.data.split(":")[1])
    avatar = await avatar_repo.get_by_id(session, avatar_id)

    if avatar is None:
        await callback.answer("Аватар не найден, попробуйте снова.")
        return

    await user_repo.set_avatar(session, callback.from_user.id, avatar_id)
    await state.set_state(BotStates.chatting)
    await state.update_data(avatar_id=avatar_id)

    await callback.message.edit_text(
        f"\u2705 Вы выбрали: <b>{avatar.name}</b>\n"
        f"<i>{avatar.description}</i>\n\n"
        "Начните разговор — просто напишите сообщение!\n"
        "Доступные команды: /history, /facts, /reset, /change_avatar",
        parse_mode="HTML",
    )
    await callback.answer()
