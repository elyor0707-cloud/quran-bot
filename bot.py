import requests
import os
import sqlite3
import random
import openai
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup

# ======================
# CONFIG
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

translator_users = {}

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
    score INTEGER DEFAULT 0,
    translator_used INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score,translator_used FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1,0,0,0
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

def activate_premium(user_id):
    cursor.execute("UPDATE users SET premium=1 WHERE user_id=?", (user_id,))
    conn.commit()

def add_translator_use(user_id):
    cursor.execute("UPDATE users SET translator_used = translator_used + 1 WHERE user_id=?", (user_id,))
    conn.commit()

# ======================
# MENU (GRID)
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

main_keyboard.add("📖 Бугунги оят","📘 Араб алифбоси")
main_keyboard.add("🧠 Тест режими","📊 Статистика")
main_keyboard.add("📚 Грамматика","💎 Premium")
main_keyboard.add("🌍 AI Таржимон")

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# AI TRANSLATOR
# ======================

@dp.message_handler(lambda m: m.text=="🌍 AI Таржимон")
async def translator_mode(message: types.Message):
    translator_users[message.from_user.id] = True
    await message.answer("🎙 Овоз хабар юборинг. Мен таржима қилиб бераман.")

@dp.message_handler(content_types=types.ContentType.VOICE)
async def voice_handler(message: types.Message):

    if message.from_user.id not in translator_users:
        return

    user_id = message.from_user.id
    ayah_index,premium,score,used = get_user(user_id)

    if premium==0 and used>=5:
        await message.answer("Free лимит тугади. Premium олинг.")
        return

    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    downloaded = await bot.download_file(file_path)

    with open("voice.ogg","wb") as f:
        f.write(downloaded.read())

    # Speech to text
    with open("voice.ogg","rb") as audio:
        transcript = openai.Audio.transcribe("whisper-1",audio)

    text = transcript["text"]

    # Translate to English (ўзгартириш мумкин)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"Translate to English"},
            {"role":"user","content":text}
        ]
    )

    translated = response["choices"][0]["message"]["content"]

    # Text to speech
    speech = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=translated
    )

    with open("translated.mp3","wb") as f:
        f.write(speech.content)

    await message.answer_audio(open("translated.mp3","rb"))

    add_translator_use(user_id)

# ======================
# TEST SYSTEM (10)
# ======================

arabic_letters = [l[0] for l in [
("ا","Алиф","а"),
("ب","Ба","б"),
("ت","Та","т"),
("ث","Са","с"),
("ج","Жим","ж"),
("ح","Ҳа","ҳ"),
("خ","Хо","х"),
("د","Дал","д"),
("ر","Ро","р"),
("م","Мим","м"),
("ي","Йа","й"),
]]

tests = {}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id] = {"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q = random.choice(arabic_letters)
    tests[message.from_user.id]["correct"] = q
    tests[message.from_user.id]["count"] += 1
    await message.answer(f"{tests[message.from_user.id]['count']}/10\nБу қайси ҳарф?\n\n{q}")

@dp.message_handler(lambda m: m.from_user.id in tests)
async def check_answer(message: types.Message):
    user_test = tests[message.from_user.id]
    if message.text.strip()==user_test["correct"]:
        user_test["score"] +=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user_test['correct']}")

    if user_test["count"]<10:
        await ask_question(message)
    else:
        final_score=user_test["score"]
        add_score(message.from_user.id, final_score*10)

        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🏠 Бош меню")

        await message.answer(
            f"🏁 Тест тугади!\n\nНатижа: {final_score}/10\nБалл: {final_score*10}",
            reply_markup=kb
        )

        del tests[message.from_user.id]

@dp.message_handler(lambda m: m.text=="🏠 Бош меню")
async def home(message: types.Message):
    translator_users.pop(message.from_user.id,None)
    await message.answer("Бош меню",reply_markup=main_keyboard)

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text=="💎 Premium")
async def premium_info(message: types.Message):
    await message.answer("""
💎 Premium:

✔ 20 та оят
✔ Чексиз AI таржимон
✔ Сертификат
✔ Статистика

Нархи: 30 USD
""")
    activate_premium(message.from_user.id)

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
