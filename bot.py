import os
import json
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
arabic_letters = [
    "ا — Алиф",
    "ب — Ба",
    "ت — Та",
    "ث — Са",
    "ج — Жим",
    "ح — Ҳа",
    "خ — Хо"
]


# TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# QURAN JSON yuklash
# ======================
with open("quran.json", "r", encoding="utf-8") as f:
    quran = json.load(f)

# ======================
# Keyboard
# ======================
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

keyboard.add(KeyboardButton("📖 Бугунги оят"))
keyboard.add(KeyboardButton("📘 Араб алифбоси"))
keyboard.add(KeyboardButton("📚 Грамматика"))
keyboard.add(KeyboardButton("🕌 Қуръон ўқиш"))
keyboard.add(KeyboardButton("💎 Premium"))


# ======================
# START
# ======================
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        "Ассалому алайкум!\nБугунги оятни олиш учун тугмани босинг.",
        reply_markup=keyboard
    )
@dp.message_handler(lambda message: message.text == "📘 Араб алифбоси")
async def arabic_lesson(message: types.Message):

    text = "📘 Араб алифбоси:\n\n"

    for letter in arabic_letters:
        text += letter + "\n"

    await message.answer(text)

# ======================
# BUGUNGI OYAT
# ======================
@dp.message_handler(lambda message: message.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    today = datetime.now().date()
    start_date = datetime(2026, 1, 1).date()  # бошланиш санаси

    days_passed = (today - start_date).days
    start_index = days_passed * 5
    end_index = start_index + 5

    if start_index >= len(quran):
        await message.answer("Қуръон тўлиқ ўқиб бўлинди 🤲")
        return

    ayahs = quran[start_index:end_index]

    text = "📖 Бугунги 5 та оят:\n\n"

    for ayah in ayahs:
        text += f"{ayah['sura']}:{ayah['ayah']} — {ayah['text']}\n\n"

    await message.answer(text)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
