import sqlite3
import os
import json
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
def generate_ayah_image(arabic_text, filename="ayah.png"):
    width = 1200
    height = 400

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    try:
       font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(arabic_text, font=font)

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    draw.text((x, y), arabic_text, fill="black", font=font)

    img.save(filename)


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

    start_index = 0
    end_index = 5

    ayahs = quran[start_index:end_index]

    for ayah in ayahs:

       generate_ayah_image(ayah['arabic'])

        
        with open("ayah.png", "rb") as photo:
        await message.answer_photo(photo)

       
        await message.answer(f"{ayah['sura']}:{ayah['ayah']}")
        await message.answer(ayah['text'])

       
        sura = str(ayah['sura']).zfill(3)
        ayah_number = str(ayah['ayah']).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"

        await message.answer_audio(audio_url)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
