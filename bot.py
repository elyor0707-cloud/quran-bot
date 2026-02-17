from aiogram import Bot, Dispatcher, executor, types
import os
from database import init_db, get_user

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

init_db()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("📖 Қуръон ёдлаш платформасига хуш келибсиз.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
