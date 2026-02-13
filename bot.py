import sqlite3
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
# DATABASE
# ======================
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    progress INTEGER DEFAULT 0
)
""")

conn.commit()

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
def get_progress(user_id):
    cursor.execute("SELECT progress FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        cursor.execute(
            "INSERT INTO users (user_id, progress) VALUES (?, ?)",
            (user_id, 0)
        )
        conn.commit()
        return 0


def save_progress(user_id, value):
    cursor.execute(
        "UPDATE users SET progress=? WHERE user_id=?",
        (value, user_id)
    )
    conn.commit()


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

    user_id = message.from_user.id

    start_index = get_progress(user_id)
    end_index = start_index + 5

    if start_index >= len(quran):
        await message.answer("Қуръон тўлиқ ўқиб бўлинди 🤲")
        return

    ayahs = quran[start_index:end_index]

    text = "📖 Бугунги 5 та оят:\n\n"

    for ayah in ayahs:
        text += f"{ayah['sura']}:{ayah['ayah']}\n"
        text += f"{ayah['text']}\n\n"

    save_progress(user_id, end_index)

    await message.answer(text)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
