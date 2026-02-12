import os
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Ассалому алайкум! Қуръон ўрганиш ботимизга хуш келибсиз.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
