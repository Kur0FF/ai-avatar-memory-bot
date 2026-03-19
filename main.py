import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from config import settings
from database.engine import async_session_factory
from database.init_db import create_tables_and_seed
from handlers import chat, commands, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseSessionMiddleware:
    """Inject AsyncSession into every handler via data['session']."""

    async def __call__(self, handler, event: Update, data: dict):
        async with async_session_factory() as session:
            data["session"] = session
            return await handler(event, data)


async def main() -> None:
    logger.info("Initializing database…")
    await create_tables_and_seed()

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register session middleware on all updates
    dp.update.middleware(DatabaseSessionMiddleware())

    # Register routers — order matters: chat last (catches all text)
    dp.include_router(start.router)
    dp.include_router(commands.router)
    dp.include_router(chat.router)

    logger.info("Starting bot polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
