from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models import Avatar


def build_avatar_keyboard(avatars: list[Avatar]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{avatar.name}",
                callback_data=f"avatar:{avatar.id}",
            )
        ]
        for avatar in avatars
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
