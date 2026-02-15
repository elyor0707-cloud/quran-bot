import requests
import os
import sqlite3
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from gtts import gTTS
from openai import OpenAI

# ======================
# CONFIG
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

ai_client = OpenAI(api_key=OPENAI_API_KEY)

# ======================
# DATABASE
# ======================

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ayah_progress INTEGER DEFAULT 1,
    premium INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1,0,0
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value,user_id))
    conn.commit()

def add_score(user_id, points):
    ayah,premium,score = get_user(user_id)

    if premium == 1:
        points = points * 2

    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

# ======================
# MAIN MENU
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
main_keyboard.add(
    "📖 Бугунги оят","📘 Араб алифбоси",
    "📊 Статистика","📚 Грамматика",
    "🧠 Тест режими","🏆 Leaderboard",
    "🌍 AI Translator","📘 Академик грамматика",
    "💎 Premium"
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!",reply_markup=main_keyboard)

# ======================
# AI TRANSLATOR (Production)
# ======================

translator_mode = {}

@dp.message_handler(lambda m: m.text=="🌍 AI Translator")
async def translator_start(message: types.Message):
    translator_mode[message.from_user.id] = True
    await message.answer("Матнни ўзбекча ёзинг. Мен арабчага таржима қиламан.\n\n🏠 Бош меню — чиқиш")

@dp.message_handler(lambda m: m.from_user.id in translator_mode)
async def translator_process(message: types.Message):

    if message.text == "🏠 Бош меню":
        del translator_mode[message.from_user.id]
        await message.answer("🏠 Бош меню", reply_markup=main_keyboard)
        return

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Professional translator Uzbek to Arabic"},
                {"role":"user","content":message.text}
            ]
        )

        translated = response.choices[0].message.content

        await message.answer(f"🌍 Арабча:\n\n{translated}")

    except Exception as e:
        await message.answer("AI хизмат ишламаяпти.")

# ======================
# BUGUNGI OYAT
# ======================

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)

    limit = 5 if premium==0 else 20

    for i in range(ayah_index,ayah_index+limit):

        response = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{i}/editions/quran-uthmani,uz.sodik"
        )

        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']
        surah = data['data'][0]['surah']['englishName']
        ayah_no = data['data'][0]['numberInSurah']

        await message.answer(f"{surah} сураси {ayah_no}-оят")
        await message.answer(arabic)
        await message.answer(uzbek)

        sura = str(data['data'][0]['surah']['number']).zfill(3)
        ayah_number = str(ayah_no).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"

        await message.answer_audio(audio_url)

    update_progress(user_id,ayah_index+limit)

# ======================
# LEADERBOARD (username)
# ======================

@dp.message_handler(lambda m: m.text=="🏆 Leaderboard")
async def leaderboard(message: types.Message):

    cursor.execute("SELECT user_id,score FROM users ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    text="🏆 ТОП 10\n\n"

    for i,row in enumerate(rows,1):
        try:
            user = await bot.get_chat(row[0])
            name = user.first_name
        except:
            name = row[0]

        text+=f"{i}. {name} — {row[1]} XP\n"

    await message.answer(text)

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text=="💎 Premium")
async def premium(message: types.Message):
    await message.answer("""
💎 Premium:

✔ 20 та оят/кун
✔ XP ×2
✔ Кенгайтирилган тест
✔ Сертификат
""")

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
