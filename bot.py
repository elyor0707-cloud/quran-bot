import requests
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
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), arabic_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

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
current_letter = {}

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
  {
    "id": 1,
    "harf": "ا",
    "nomi": "Alif",
    "talaffuz": "Halqum boshidan chiqadi",
    "shakllar": {
      "alohida": "ا",
      "boshida": "ا",
      "ortasida": "ـا",
      "oxirida": "ـا"
    },
    "misollar": [
      "اَللّٰه",
      "اِيمَان"
    ],
    "tajwid": "Madd harfi bo‘lishi mumkin"
  }
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

    index = 0
    letter = arabic_letters[index]

    current_letter[message.from_user.id] = index

    text = f"""
📘 Ҳарф: {letter['letter']}

🔤 Номи: {letter['name']}
🗣 Талаффуз: {letter['pronunciation']}
📖 Ўқилиши: {letter['reading']}

📌 Сўз бошида: {letter['begin']}
📌 Сўз ўртасида: {letter['middle']}
📌 Сўз охирида: {letter['end']}

🕌 Қуръондан мисол: {letter['example']}
"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➡ Кейинги ҳарф")
    keyboard.add("🔊 Талаффуз аудио")

    await message.answer(text, reply_markup=keyboard)
@dp.message_handler(lambda message: message.text == "➡ Кейинги ҳарф")
async def next_letter(message: types.Message):

    user_id = message.from_user.id

    index = current_letter.get(user_id, 0) + 1

    if index >= len(arabic_letters):
        await message.answer("🎉 Алифбо тугади!")
        return

    current_letter[user_id] = index
    letter = arabic_letters[index]

    text = f"""
📘 Ҳарф: {letter['letter']}

🔤 Номи: {letter['name']}
🗣 Талаффуз: {letter['pronunciation']}
📖 Ўқилиши: {letter['reading']}

📌 Сўз бошида: {letter['begin']}
📌 Сўз ўртасида: {letter['middle']}
📌 Сўз охирида: {letter['end']}

🕌 Қуръондан мисол: {letter['example']}
"""

    await message.answer(text)
@dp.message_handler(lambda message: message.text == "🔊 Талаффуз аудио")
async def letter_audio(message: types.Message):

    user_id = message.from_user.id
    index = current_letter.get(user_id, 0)

    letter = arabic_letters[index]

    await message.answer_audio(letter["audio"])


# ======================
# BUGUNGI 5 OYAT
# ======================
@dp.message_handler(lambda message: message.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    for i in range(1, 6):  # 5 та оят

        response = requests.get(f"https://api.alquran.cloud/v1/ayah/{i}/editions/quran-uthmani,uz.sodik")
        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']

        await message.answer(f"{i}-оят")
        await message.answer(arabic)
        await message.answer(uzbek)

        sura = str(data['data'][0]['surah']['number']).zfill(3)
        ayah_number = str(data['data'][0]['numberInSurah']).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"
        await message.answer_audio(audio_url)



# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
