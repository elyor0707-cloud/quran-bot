import requests
import os
import sqlite3
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from gtts import gTTS
import tempfile

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
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

def activate_premium(user_id):
    cursor.execute("UPDATE users SET premium=1 WHERE user_id=?", (user_id,))
    conn.commit()

# ======================
# MAIN MENU
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_keyboard.add(
    "📖 Бугунги оят",
    "📘 Араб алифбоси",
    "📊 Статистика",
    "📚 Грамматика",
    "🧠 Тест режими",
    "🌍 AI Таржимон",
    "💎 Platinum"
)

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ARABIC LETTERS (28 + AUDIO)
# ======================

arabic_letters = [
("ا","Алиф","а","ا","ـا","ـا","اللّٰه","alif.mp3"),
("ب","Ба","б","بـ","ـبـ","ـب","بسم","ba.mp3"),
("ت","Та","т","تـ","ـتـ","ـت","توبة","ta.mp3"),
("ث","Са","с","ثـ","ـثـ","ـث","ثواب","tha.mp3"),
("ج","Жим","ж","جـ","ـجـ","ـج","جنة","jeem.mp3"),
("ح","Ҳа","ҳ","حـ","ـحـ","ـح","حق","ha.mp3"),
("خ","Хо","х","خـ","ـخـ","ـخ","خلق","kha.mp3"),
("د","Дал","д","د","ـد","ـد","دين","dal.mp3"),
("ذ","Зал","з","ذ","ـذ","ـذ","ذكر","dhal.mp3"),
("ر","Ро","р","ر","ـر","ـر","رحمن","ra.mp3"),
("ز","Зай","з","ز","ـز","ـز","زكاة","zay.mp3"),
("س","Син","с","سـ","ـسـ","ـس","سلام","seen.mp3"),
("ش","Шин","ш","شـ","ـشـ","ـش","شمس","sheen.mp3"),
("ص","Сод","с","صـ","ـصـ","ـص","صلاة","sad.mp3"),
("ض","Дод","д","ضـ","ـضـ","ـض","ضلال","dad.mp3"),
("ط","То","т","طـ","ـطـ","ـط","طاعة","ta2.mp3"),
("ظ","Зо","з","ظـ","ـظـ","ـظ","ظلم","za.mp3"),
("ع","Айн","ъ","عـ","ـعـ","ـع","علم","ain.mp3"),
("غ","Ғайн","ғ","غـ","ـغـ","ـغ","غفور","ghain.mp3"),
("ف","Фа","ф","فـ","ـفـ","ـف","فجر","fa.mp3"),
("ق","Қоф","қ","قـ","ـقـ","ـق","قرآن","qaf.mp3"),
("ك","Каф","к","كـ","ـكـ","ـك","كتاب","kaf.mp3"),
("ل","Лам","л","لـ","ـلـ","ـل","الله","lam.mp3"),
("م","Мим","м","مـ","ـمـ","ـم","ملك","meem.mp3"),
("ن","Нун","н","نـ","ـنـ","ـن","نور","noon.mp3"),
("ه","Ҳа","ҳ","هـ","ـهـ","ـه","هدى","ha2.mp3"),
("و","Вов","в","و","ـو","ـو","وعد","waw.mp3"),
("ي","Йа","й","يـ","ـيـ","ـي","يوم","ya.mp3"),
]

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🔊 Ўқилиш аудио","🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:", reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):
    letter = next(l for l in arabic_letters if l[0]==message.text)
    await message.answer(f"""
📘 Ҳарф: {letter[0]}

🔤 Номи: {letter[1]}
📖 Ўқилиши: {letter[2]}

📌 Бошида: {letter[3]}
📌 Ўртасида: {letter[4]}
📌 Охирида: {letter[5]}

🕌 Мисол: {letter[6]}
""")

# ======================
# AI REALTIME TRANSLATOR
# ======================

@dp.message_handler(lambda m: m.text == "🌍 AI Таржимон")
async def translator_info(message: types.Message):
    await message.answer("Овозли хабар юборинг. Мен таржима қилиб аудио қайтарман.")

@dp.message_handler(content_types=types.ContentType.VOICE)
async def voice_translate(message: types.Message):
    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "voice.ogg")

    # Бу ерда реал AI STT интеграция қилиш мумкин
    text = "Салом дунё"  # placeholder

    translated = "Hello world"

    tts = gTTS(translated, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        await message.answer_audio(open(f.name, "rb"))

# ======================
# GRAMMAR
# ======================

@dp.message_handler(lambda m: m.text == "📚 Грамматика")
async def grammar(message: types.Message):
    await message.answer("""
📚 Араб грамматикаси (Кенгайтирилган):

1️⃣ Ҳаракатлар — фатҳа, касра, дамма
2️⃣ Танвин — ан, ин, ун
3️⃣ Сукун — ْ
4️⃣ Шадда — ّ
5️⃣ Исм, феъл, ҳарф
6️⃣ Музаккар / Мунасс
7️⃣ Жумла турлари
8️⃣ Иъроб асослари
""")

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text == "💎 Platinum")
async def premium(message: types.Message):
    activate_premium(message.from_user.id)
    await message.answer("💎 Platinum фаоллаштирилди!")

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
