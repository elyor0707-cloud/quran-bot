import requests
import os
import sqlite3
import random
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
        points *= 2
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
    "💎 Premium"
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!",reply_markup=main_keyboard)

@dp.message_handler(lambda m: m.text=="🏠 Бош меню")
async def home(message: types.Message):
    await message.answer("🏠 Бош меню",reply_markup=main_keyboard)

# ======================
# BUGUNGI OYAT (NAVIGATION + AUDIO)
# ======================

def ayah_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    kb.add("⬅️ Олдинги оят","➡️ Кейинги оят")
    kb.add("🏠 Бош меню")
    return kb

async def send_ayah(message, ayah_number):
    response = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{ayah_number}/editions/quran-uthmani,uz.sodik"
    )
    data = response.json()

    arabic = data['data'][0]['text']
    uzbek = data['data'][1]['text']
    surah = data['data'][0]['surah']['englishName']
    ayah_no = data['data'][0]['numberInSurah']

    await message.answer(f"{surah} сураси {ayah_no}-оят",reply_markup=ayah_keyboard())
    await message.answer(arabic)
    await message.answer(uzbek)

    sura = str(data['data'][0]['surah']['number']).zfill(3)
    ayah_num = str(ayah_no).zfill(3)
    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"
    await message.answer_audio(audio_url)

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)
    await send_ayah(message,ayah_index)

@dp.message_handler(lambda m: m.text=="➡️ Кейинги оят")
async def next_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)
    ayah_index += 1
    update_progress(user_id,ayah_index)
    await send_ayah(message,ayah_index)

@dp.message_handler(lambda m: m.text=="⬅️ Олдинги оят")
async def prev_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)
    if ayah_index>1:
        ayah_index -= 1
        update_progress(user_id,ayah_index)
    await send_ayah(message,ayah_index)

# ======================
# ARABIC ALPHABET (28 LETTERS)
# ======================

arabic_letters = [
("ا","Алиф","а"),("ب","Ба","б"),("ت","Та","т"),("ث","Са","с"),
("ج","Жим","ж"),("ح","Ҳа","ҳ"),("خ","Хо","х"),("د","Дал","д"),
("ذ","Зал","з"),("ر","Ро","р"),("ز","Зай","з"),("س","Син","с"),
("ش","Шин","ш"),("ص","Сод","с"),("ض","Дод","д"),("ط","То","т"),
("ظ","Зо","з"),("ع","Айн","ъ"),("غ","Ғайн","ғ"),("ف","Фа","ф"),
("ق","Қоф","қ"),("ك","Каф","к"),("ل","Лам","л"),("م","Мим","м"),
("ن","Нун","н"),("ه","Ҳа","ҳ"),("و","Вов","в"),("ي","Йа","й"),
]

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text=="📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:",reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):
    letter = next(l for l in arabic_letters if l[0]==message.text)
    await message.answer(
        f"Ҳарф: {letter[0]}\nНоми: {letter[1]}\nЎқилиши: {letter[2]}",
        reply_markup=alphabet_keyboard()
    )

# ======================
# STATISTICS
# ======================

@dp.message_handler(lambda m: m.text=="📊 Статистика")
async def stats(message: types.Message):
    ayah,premium,score = get_user(message.from_user.id)
    await message.answer(
        f"📖 Оят индекси: {ayah}\n⭐ Балл: {score}\n💎 Premium: {'Ҳа' if premium==1 else 'Йўқ'}"
    )

# ======================
# TEST MODE (OLD WORKING VERSION)
# ======================

tests = {}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id]={"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q=random.choice(arabic_letters)
    tests[message.from_user.id]["correct"]=q[2]
    tests[message.from_user.id]["count"]+=1
    kb=ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("❌ Тестни тугатиш","🏠 Бош меню")
    await message.answer(f"{tests[message.from_user.id]['count']}/10\n{q[0]}",reply_markup=kb)

@dp.message_handler(lambda m: m.text=="❌ Тестни тугатиш")
async def stop_test(message: types.Message):
    if message.from_user.id in tests:
        del tests[message.from_user.id]
    await message.answer("Тест тугатилди",reply_markup=main_keyboard)

@dp.message_handler(lambda m: m.from_user.id in tests and m.text not in ["❌ Тестни тугатиш","🏠 Бош меню"])
async def check_answer(message: types.Message):
    user=tests[message.from_user.id]
    if message.text.lower()==user["correct"]:
        user["score"]+=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user['correct']}")
    if user["count"]<10:
        await ask_question(message)
    else:
        final=user["score"]
        add_score(message.from_user.id,final*10)
        await message.answer(f"🏁 Натижа: {final}/10",reply_markup=main_keyboard)
        del tests[message.from_user.id]

# ======================
# LEADERBOARD
# ======================

@dp.message_handler(lambda m: m.text=="🏆 Leaderboard")
async def leaderboard(message: types.Message):
    cursor.execute("SELECT user_id,score FROM users ORDER BY score DESC LIMIT 10")
    rows=cursor.fetchall()
    text="🏆 ТОП 10\n\n"
    for i,row in enumerate(rows,1):
        text+=f"{i}. {row[0]} — {row[1]} XP\n"
    await message.answer(text)

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text=="💎 Premium")
async def premium(message: types.Message):
    await message.answer(
        "💎 Premium:\n✔ 20 та оят/кун\n✔ XP ×2\n\nАктив қилиш учун админга мурожаат қилинг."
    )

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
