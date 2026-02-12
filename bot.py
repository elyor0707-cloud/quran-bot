import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(message: Message):
        await message.answer("Ассалому алайкум! Қуръон ўрганиш ботимизга хуш келибсиз.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
