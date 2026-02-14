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
    premium INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress, premium FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1, 0
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

# ======================
# ARABIC LETTERS
# ======================

arabic_letters = [
{"letter":"ا","name":"Алиф","reading":"а"},
{"letter":"ب","name":"Ба","reading":"б"},
{"letter":"ت","name":"Та","reading":"т"},
{"letter":"ث","name":"Са","reading":"с"},
{"letter":"ج","name":"Жим","reading":"ж"},
{"letter":"ح","name":"Ҳа","reading":"ҳ"},
{"letter":"خ","name":"Хо","reading":"х"},
{"letter":"د","name":"Дал","reading":"д"},
{"letter":"ذ","name":"Зал","reading":"з"},
{"letter":"ر","name":"Ро","reading":"р"},
{"letter":"ز","name":"Зай","reading":"з"},
{"letter":"س","name":"Син","reading":"с"},
{"letter":"ش","name":"Шин","reading":"ш"},
{"letter":"ص","name":"Сод","reading":"с"},
{"letter":"ض","name":"Дод","reading":"д"},
{"letter":"ط","name":"То","reading":"т"},
{"letter":"ظ","name":"Зо","reading":"з"},
{"letter":"ع","name":"Айн","reading":"ъ"},
{"letter":"غ","name":"Ғайн","reading":"ғ"},
{"letter":"ف","name":"Фа","reading":"ф"},
{"letter":"ق","name":"Қоф","reading":"қ"},
{"letter":"ك","name":"Каф","reading":"к"},
{"letter":"ل","name":"Лам","reading":"л"},
{"letter":"م","name":"Мим","reading":"м"},
{"letter":"ن","name":"Нун","reading":"н"},
{"letter":"ه","name":"Ҳа","reading":"ҳ"},
{"letter":"و","name":"Вов","reading":"в"},
{"letter":"ي","name":"Йа","reading":"й"}
]

# ======================
# MENUS
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("📖 Бугунги оят")
main_keyboard.add("📘 Араб алифбоси")
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
""")

# ======================
# TODAY AYAH (PROGRESS SYSTEM)
# ======================

@dp.message_handler(lambda m: m.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index, premium = get_user(user_id)

    limit = 5
    if premium == 1:
        limit = 20

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
# GRAMMAR
# ======================

@dp.message_handler(lambda m: m.text == "📚 Грамматика")
async def grammar(message: types.Message):
    await message.answer("""
📚 Араб грамматикаси:

1️⃣ Ҳаракатлар
2️⃣ Танвин
3️⃣ Сукун
4️⃣ Шадда
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
# HOME
# ======================

@dp.message_handler(lambda m: m.text == "🏠 Уйга қайтиш")
async def go_home(message: types.Message):
    await message.answer("Бош меню", reply_markup=main_keyboard)

# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
