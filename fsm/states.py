from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    choosing_avatar = State()
    chatting = State()
