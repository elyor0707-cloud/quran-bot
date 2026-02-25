"""
🕌 Qur'on va Arab tili o'rgatuvchi Telegram Bot
Qori: Mishary Rashid al-Afasy
"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, alphabet, grammar, tajwid, quran, quran_read, test, progress
from handlers import quran
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(alphabet.router)
    dp.include_router(grammar.router)
    dp.include_router(tajwid.router)
    dp.include_router(quran.router)
    dp.include_router(quran_read.router)
    dp.include_router(test.router)
    dp.include_router(progress.router)

    await bot.delete_webhook(drop_pending_updates=True)

    print("🕌 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
