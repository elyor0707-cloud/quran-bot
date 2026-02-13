import os
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📚 Араб алифбоси")
    keyboard.add("📖 Грамматика")
    keyboard.add("🕌 Қуръон ўқиш")
    keyboard.add("💎 Premium")

    await message.answer(
        "Ассалому алайкум!\nҚайси бўлимни танлайсиз?",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "📚 Араб алифбоси")
async def alphabet_section(message: types.Message):
    await message.answer(
        "📚 Араб алифбоси бўлими\n\n"
        "1️⃣ Алиф\n"
        "2️⃣ Ба\n"
        "3️⃣ Та\n\n"
        "Тез кунда интерактив дарслар қўшилади."
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
