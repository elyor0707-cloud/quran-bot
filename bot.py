import requests
import sqlite3
import os
import json
from PIL import Image, ImageDraw, ImageFont
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
    ayah_progress INTEGER DEFAULT 0,
    letter_progress INTEGER DEFAULT 0
)
""")
conn.commit()

# ======================
# QURAN JSON yuklash
# ======================
with open("quran.json", "r", encoding="utf-8") as f:
    quran = json.load(f)

# ======================
# ARAB LETTERS JSON yuklash
# ======================
with open("arab_letters.json", "r", encoding="utf-8") as f:
    arabic_letters = json.load(f)

# ======================
# PROGRESS FUNCTIONS
# ======================
def get_user(user_id):
    cursor.execute("SELECT ayah_progress, letter_progress FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 0, 0
    return user

def update_letter_progress(user_id):
    cursor.execute("UPDATE users SET letter_progress = letter_progress + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def update_ayah_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

# ======================
# IMAGE GENERATOR
# ======================
def generate_letter_image(letter):
    width, height = 800, 800
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_big = ImageFont.truetype("DejaVuSans.ttf", 250)
    font_mid = ImageFont.truetype("DejaVuSans.ttf", 120)
    font_small = ImageFont.truetype("DejaVuSans.ttf", 60)

    draw.text((400, 200), letter["harf"], font=font_big, fill="black", anchor="mm")

    shapes = f"{letter['shakllar']['boshida']}   {letter['shakllar']['ortasida']}   {letter['shakllar']['oxirida']}"
    draw.text((400, 400), shapes, font=font_mid, fill="black", anchor="mm")

    draw.text((400, 550), letter["misollar"][0], font=font_mid, fill="black", anchor="mm")

    draw.text((400, 700), letter["talaffuz"], font=font_small, fill="gray", anchor="mm")

    filename = "letter.png"
    img.save(filename)
    return filename

# ======================
# KEYBOARD
# ======================
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("📖 Бугунги оят"))
main_keyboard.add(KeyboardButton("📘 Араб алифбоси"))

# ======================
# START
# ======================
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ARAB ALPHABET
# ======================
@dp.message_handler(lambda message: message.text == "📘 Араб алифбоси")
async def arabic_lesson(message: types.Message):

    user_id = message.from_user.id
    _, letter_index = get_user(user_id)

    if letter_index >= len(arabic_letters):
        await message.answer("🎉 Алифбо тугади!")
        return

    letter = arabic_letters[letter_index]
    image_path = generate_letter_image(letter)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➡ Кейинги ҳарф")
    keyboard.add("🔊 Талаффуз аудио")
    keyboard.add("⬅ Орқага")

    await message.answer_photo(open(image_path, "rb"), reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "➡ Кейинги ҳарф")
async def next_letter(message: types.Message):
    user_id = message.from_user.id
    update_letter_progress(user_id)
    await arabic_lesson(message)

@dp.message_handler(lambda message: message.text == "🔊 Талаффуз аудио")
async def letter_audio(message: types.Message):
    user_id = message.from_user.id
    _, letter_index = get_user(user_id)

    if letter_index < len(arabic_letters):
        letter = arabic_letters[letter_index]
        if "audio" in letter:
            await message.answer_audio(letter["audio"])
        else:
            await message.answer("Аудио мавжуд эмас.")

# ======================
# BUGUNGI 5 OYAT
# ======================
@dp.message_handler(lambda message: message.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index, _ = get_user(user_id)

    for i in range(5):
        if ayah_index + i >= len(quran):
            break

        ayah = quran[ayah_index + i]
        arabic = ayah["text"]

        await message.answer(f"{ayah['surah']}:{ayah['ayah']}")
        await message.answer(arabic)

        generate_ayah_image(arabic)
        await message.answer_photo(open("ayah.png", "rb"))

    update_ayah_progress(user_id, ayah_index + 5)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
