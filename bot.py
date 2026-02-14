import requests
import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup

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
    score INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_active TEXT
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score,streak,last_active FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1,0,0,0,None
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score = score + ? WHERE user_id=?", (points,user_id))
    conn.commit()

def update_streak(user_id):
    today = str(datetime.now().date())
    cursor.execute("SELECT last_active, streak FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        last, streak = row
        if last != today:
            streak += 1
            cursor.execute("UPDATE users SET streak=?, last_active=? WHERE user_id=?", (streak,today,user_id))
            conn.commit()

# ======================
# ARABIC LETTERS FULL
# ======================

arabic_letters = [
{"letter":"ا","name":"Алиф","reading":"а","begin":"ا","middle":"ـا","end":"ـا","example":"اللّٰه"},
{"letter":"ب","name":"Ба","reading":"б","begin":"بـ","middle":"ـبـ","end":"ـب","example":"بسم"},
{"letter":"ت","name":"Та","reading":"т","begin":"تـ","middle":"ـتـ","end":"ـت","example":"توبة"},
{"letter":"ث","name":"Са","reading":"с","begin":"ثـ","middle":"ـثـ","end":"ـث","example":"ثواب"},
{"letter":"ج","name":"Жим","reading":"ж","begin":"جـ","middle":"ـجـ","end":"ـج","example":"جنة"},
{"letter":"ح","name":"Ҳа","reading":"ҳ","begin":"حـ","middle":"ـحـ","end":"ـح","example":"حق"},
{"letter":"خ","name":"Хо","reading":"х","begin":"خـ","middle":"ـخـ","end":"ـخ","example":"خلق"},
{"letter":"د","name":"Дал","reading":"д","begin":"د","middle":"ـد","end":"ـد","example":"دين"},
{"letter":"ر","name":"Ро","reading":"р","begin":"ر","middle":"ـر","end":"ـر","example":"رحمن"},
{"letter":"م","name":"Мим","reading":"м","begin":"مـ","middle":"ـمـ","end":"ـم","example":"ملك"},
{"letter":"ي","name":"Йа","reading":"й","begin":"يـ","middle":"ـيـ","end":"ـي","example":"يوم"}
]

# ======================
# MENUS
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("📖 Бугунги оят")
main_keyboard.add("📘 Араб алифбоси")
main_keyboard.add("🧠 Тест режими")
main_keyboard.add("📊 Статистика")
main_keyboard.add("📚 Грамматика")
main_keyboard.add("💎 Premium")

def alphabet_table():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=7)
    letters = [l["letter"] for l in arabic_letters]
    kb.add(*letters)
    kb.add("🏠 Уйга қайтиш")
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ALPHABET TABLE
# ======================

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:", reply_markup=alphabet_table())

@dp.message_handler(lambda m: m.text in [l["letter"] for l in arabic_letters])
async def letter_info(message: types.Message):
    letter = next(l for l in arabic_letters if l["letter"] == message.text)
    await message.answer(f"""
📘 Ҳарф: {letter['letter']}

🔤 Номи: {letter['name']}
📖 Ўқилиши: {letter['reading']}

📌 Сўз бошида: {letter['begin']}
📌 Сўз ўртасида: {letter['middle']}
📌 Сўз охирида: {letter['end']}

🕌 Мисол: {letter['example']}
""")

# ======================
# TEST MODE
# ======================

@dp.message_handler(lambda m: m.text == "🧠 Тест режими")
async def test_mode(message: types.Message):
    import random
    letter = random.choice(arabic_letters)
    await message.answer(f"Бу қайси ҳарф?\n\n{letter['letter']}")
    current_test[message.from_user.id] = letter["reading"]

current_test = {}

@dp.message_handler(lambda m: m.from_user.id in current_test)
async def check_test(message: types.Message):
    correct = current_test[message.from_user.id]
    if message.text.lower() == correct:
        add_score(message.from_user.id,10)
        await message.answer("✅ Тўғри! +10 балл")
    else:
        await message.answer(f"❌ Нотўғри. Тўғри жавоб: {correct}")
    del current_test[message.from_user.id]

# ======================
# TODAY AYAH
# ======================

@dp.message_handler(lambda m: m.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index, premium, score, streak, last_active = get_user(user_id)

    update_streak(user_id)

    limit = 5 if premium == 0 else 20

    for i in range(ayah_index, ayah_index + limit):

        response = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{i}/editions/quran-uthmani,uz.sodik"
        )

        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']
        surah_name = data['data'][0]['surah']['englishName']

        await message.answer(f"{surah_name} сураси {data['data'][0]['numberInSurah']}-оят")
        await message.answer(arabic)
        await message.answer(uzbek)

        sura = str(data['data'][0]['surah']['number']).zfill(3)
        ayah_number = str(data['data'][0]['numberInSurah']).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"

        await message.answer_audio(audio_url)

    update_progress(user_id, ayah_index + limit)

# ======================
# STATISTICS
# ======================

@dp.message_handler(lambda m: m.text == "📊 Статистика")
async def stats(message: types.Message):
    ayah,premium,score,streak,last = get_user(message.from_user.id)
    await message.answer(f"""
📊 Сизнинг статистикангиз:

📖 Оят прогресс: {ayah}
⭐ Балл: {score}
🔥 Стрик: {streak} кун
💎 Premium: {"Ҳа" if premium==1 else "Йўқ"}
""")

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text == "💎 Premium")
async def premium(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("UPDATE users SET premium=1 WHERE user_id=?", (user_id,))
    conn.commit()
    await message.answer("Premium фаоллаштирилди! 🚀")

# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
