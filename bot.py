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
    "ا — Алиф — а",
    "ب — Ба — б",
    "ت — Та — т",
    "ث — Са — с",
    "ج — Жим — ж",
    "ح — Ҳа — қаттиқ ҳ",
    "خ — Хо — х",
    "د — Дал — д",
    "ذ — Зал — з",
    "ر — Ро — р",
    "ز — Зай — з",
    "س — Син — с",
    "ش — Шин — ш",
    "ص — Сод — қаттиқ с",
    "ض — Дод — қаттиқ д",
    "ط — То — қаттиқ т",
    "ظ — Зо — қаттиқ з",
    "ع — Айн — томоқ товуш",
    "غ — Ғайн — ғ",
    "ف — Фа — ф",
    "ق — Қоф — қ",
    "ك — Каф — к",
    "ل — Лам — л",
    "م — Мим — м",
    "ن — Нун — н",
    "ه — Ҳа — ҳ",
    "و — Вов — в/у",
    "ي — Йа — й/и"
]

# ======================
# TAJWID QOIDALARI
# ======================
tajwid_rules = {
    "نْ": "🟢 Нун сокин — ихфо / идғом / изҳор текширилади",
    "مْ": "🔵 Мим сокин — ихфо шафавий ёки идғом",
    "ر": "🟡 Ро — тафхим ёки тарқиқ",
    "ل": "🟣 Лом — Аллоҳ калимасида тафхим бўлиши мумкин"
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

    today = datetime.now().date()
    start_date = datetime(2026, 1, 1).date()

    days_passed = (today - start_date).days
    start_index = days_passed * 5
    end_index = start_index + 5

    ayahs = quran[start_index:end_index]

    text = "📖 Бугунги 5 та оят:\n\n"

    for ayah in ayahs:
        text += f"{ayah['sura']}:{ayah['ayah']}\n"
        text += f"{ayah['arabic']}\n"
        text += f"{ayah['text']}\n"

        sura = str(ayah['sura']).zfill(3)
        ayah_number = str(ayah['ayah']).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"

        text += f"🎧 Аудио: {audio_url}\n\n"

    await message.answer(text)



# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
