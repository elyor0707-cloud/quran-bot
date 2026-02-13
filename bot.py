import os
import json
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ======================
# TOKEN
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# QURAN JSON yuklash
# ======================
with open("quran.json", "r", encoding="utf-8") as f:
    quran = json.load(f)

# ======================
# DATA
# ======================
arabic_letters = [
    "ا — Алиф",
    "ب — Ба",
    "ت — Та",
    "ث — Са",
    "ج — Жим",
    "ح — Ҳа",
    "خ — Хо"
]

tajwid_rules = {
    "ن": "🟢 Нун — ихфо ёки идғом бўлиши мумкин",
    "م": "🔵 Мим — идғом ёки ихфо",
}

# ======================
# PROGRESS FUNCTIONS
# ======================
def save_progress(user_id, value):
    data = {}
    try:
        with open("progress.json", "r") as f:
            data = json.load(f)
    except:
        pass

    data[str(user_id)] = value

    with open("progress.json", "w") as f:
        json.dump(data, f)


def get_progress(user_id):
    try:
        with open("progress.json", "r") as f:
            data = json.load(f)
            return data.get(str(user_id), 0)
    except:
        return 0

# ======================
# KEYBOARD
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

# ======================
# ARABIC ALPHABET
# ======================
@dp.message_handler(lambda message: message.text == "📘 Араб алифбоси")
async def arabic_lesson(message: types.Message):
    text = "📘 Араб алифбоси:\n\n"
    for letter in arabic_letters:
        text += letter + "\n"
    await message.answer(text)

# ======================
# BUGUNGI 5 OYAT
# ======================
@dp.message_handler(lambda message: message.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    today = datetime.now().date()
    start_date = datetime(2026, 1, 1).date()

    days_passed = (today - start_date).days
    start_index = days_passed * 5
    end_index = start_index + 5

    if start_index >= len(quran):
        await message.answer("Қуръон тўлиқ ўқиб бўлинди 🤲")
        return

    ayahs = quran[start_index:end_index]

    save_progress(message.from_user.id, end_index)

    text = "📖 Бугунги 5 та оят:\n\n"

    for ayah in ayahs:
        text += f"{ayah['sura']}:{ayah['ayah']}\n"
        text += f"{ayah['text']}\n"

        # Tajwid tekshirish
        for letter, rule in tajwid_rules.items():
            if letter in ayah['text']:
                text += f"{rule}\n"

        text += "\n"

    await message.answer(text)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
