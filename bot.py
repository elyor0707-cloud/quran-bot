import os
import requests
import sqlite3
import random
import difflib
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from openai import OpenAI

# ======================
# TOKENS
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
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,score FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1,0
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value,user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

# ======================
# GLOBAL STATES
# ======================

recitation_mode = {}
search_mode = {}
tests = {}

# ======================
# MAIN MENU
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
main_keyboard.add(
    "📖 Бугунги оят", "🎙 Қироат текшириш",
    "📘 Араб алифбоси","🧠 Тест режими",
    "🔎 Оят қидириш"
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("📚 Қуръон ўрганиш ботiga хуш келибсиз!",reply_markup=main_keyboard)

# ======================
# QIROAT MODE
# ======================

@dp.message_handler(lambda m: m.text=="🎙 Қироат текшириш")
async def start_recitation(message: types.Message):
    recitation_mode[message.from_user.id] = True
    await message.answer("🎙 Илтимос, оятни овоз орқали юборинг.")

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):

    if message.from_user.id not in recitation_mode:
        return

    file = await bot.get_file(message.voice.file_id)
    downloaded = await bot.download_file(file.file_path)

    with open("voice.ogg","wb") as f:
        f.write(downloaded.read())

    audio_file = open("voice.ogg","rb")

    transcript = ai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ar"
    )

    spoken_text = transcript.text.strip()

    ayah_index,_ = get_user(message.from_user.id)

    r = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{ayah_index}/quran-uthmani"
    ).json()

    correct_text = r['data']['text']

    similarity = difflib.SequenceMatcher(
        None,
        spoken_text,
        correct_text
    ).ratio()

    percent = round(similarity * 100)

    if percent >= 90:
        result = "🟢 Аъло қироат!"
        add_score(message.from_user.id,20)
    elif percent >= 70:
        result = "🟡 Яхши, аммо хато бор."
        add_score(message.from_user.id,10)
    else:
        result = "🔴 Қайта ўқиш керак."

    await message.answer(f"""
📊 Қироат таҳлили:

Сизнинг ўқишингиз:
{spoken_text}

Тўғри оят:
{correct_text}

Мослик: {percent}%

{result}
""")

    del recitation_mode[message.from_user.id]

# ======================
# BUGUNGI OYAT
# ======================

def ayah_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    kb.add("⬅️ Олдинги","➡️ Кейинги")
    kb.add("🏠 Бош меню")
    return kb

async def send_ayah(message, ayah_number):
    try:
        r = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{ayah_number}/editions/quran-uthmani,uz.sodik"
        ).json()

        arabic = r['data'][0]['text']
        uzbek = r['data'][1]['text']
        surah = r['data'][0]['surah']['englishName']
        ayah_no = r['data'][0]['numberInSurah']

        await message.answer(
            f"{surah} сураси {ayah_no}-оят\n\n{arabic}\n\n{uzbek}",
            reply_markup=ayah_keyboard()
        )

    except:
        await message.answer("⚠️ Хатолик.")

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):
    ayah_index,_ = get_user(message.from_user.id)
    await send_ayah(message,ayah_index)

# ======================
# SEARCH
# ======================

@dp.message_handler(lambda m: m.text=="🔎 Оят қидириш")
async def search_start(message: types.Message):
    search_mode[message.from_user.id]=True
    await message.answer("Калит сўз киритинг:")

@dp.message_handler(lambda m: m.from_user.id in search_mode)
async def search(message: types.Message):
    keyword = message.text
    response = requests.get(
        f"https://api.alquran.cloud/v1/search/{keyword}/all/uz.sodik"
    ).json()

    if response["data"]["count"]==0:
        await message.answer("❌ Топилмади")
        del search_mode[message.from_user.id]
        return

    for ayah in response["data"]["matches"][:3]:
        await message.answer(ayah["text"])

    del search_mode[message.from_user.id]

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
