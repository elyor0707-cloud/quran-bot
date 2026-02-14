import requests
import sqlite3
import os
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

current_letter = {}

# ======================
# ARABIC LETTERS DATA
# ======================

arabic_letters = [
    {
        "letter": "ا",
        "name": "Алиф",
        "pronunciation": "А товуши",
        "reading": "а",
        "begin": "ا",
        "middle": "ـا",
        "end": "ـا",
        "example": "اللّٰه",
        "audio": "letters_audio/alif.mp3"
    },
    {
        "letter": "ب",
        "name": "Ба",
        "pronunciation": "Б товуши",
        "reading": "б",
        "begin": "بـ",
        "middle": "ـبـ",
        "end": "ـب",
        "example": "بسم",
        "audio": "letters_audio/ba.mp3"
    }
]

# ======================
# MAIN MENU
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("📖 Бугунги оят")
main_keyboard.add("📘 Араб алифбоси")

# ======================
# LETTER KEYBOARD
# ======================

def letter_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⬅ Олдинги ҳарф", "➡ Кейинги ҳарф")
    kb.add("🔊 Талаффуз аудио")
    kb.add("🏠 Уйга қайтиш")
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ARABIC ALPHABET START
# ======================

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def arabic_start(message: types.Message):
    current_letter[message.from_user.id] = 0
    await send_letter(message, 0)

# ======================
# SEND LETTER FUNCTION
# ======================

async def send_letter(message, index):
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

    await message.answer(text, reply_markup=letter_keyboard())

# ======================
# NEXT LETTER
# ======================

@dp.message_handler(lambda m: m.text == "➡ Кейинги ҳарф")
async def next_letter(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0) + 1

    if index >= len(arabic_letters):
        await message.answer("🎉 Алифбо тугади!", reply_markup=main_keyboard)
        return

    current_letter[user_id] = index
    await send_letter(message, index)

# ======================
# PREVIOUS LETTER
# ======================

@dp.message_handler(lambda m: m.text == "⬅ Олдинги ҳарф")
async def prev_letter(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0) - 1

    if index < 0:
        index = 0

    current_letter[user_id] = index
    await send_letter(message, index)

# ======================
# LETTER AUDIO
# ======================

@dp.message_handler(lambda m: m.text == "🔊 Талаффуз аудио")
async def letter_audio(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0)

    letter = arabic_letters[index]

    if os.path.exists(letter["audio"]):
        with open(letter["audio"], "rb") as audio:
            await message.answer_audio(audio)
    else:
        await message.answer("Аудио файл топилмади.")

# ======================
# HOME
# ======================

@dp.message_handler(lambda m: m.text == "🏠 Уйга қайтиш")
async def go_home(message: types.Message):
    await message.answer("Бош меню", reply_markup=main_keyboard)

# ======================
# TODAY AYAH
# ======================

@dp.message_handler(lambda m: m.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    for i in range(1, 6):
        response = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{i}/editions/quran-uthmani,uz.sodik"
        )
        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']

        await message.answer(f"{i}-оят")
        await message.answer(arabic)
        await message.answer(uzbek)

# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
