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
# SURAH SYSTEM (114)
# ======================

surah_names = [
"Al-Faatiha","Al-Baqara","Aal-Imran","An-Nisa","Al-Ma'idah",
"Al-An'am","Al-A'raf","Al-Anfal","At-Tawbah","Yunus"
]

def surah_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    for i,name in enumerate(surah_names,1):
        kb.insert(f"{i}. {name}")
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def surah_select(message: types.Message):
    await message.answer("📖 Сурани танланг:",reply_markup=surah_keyboard())

@dp.message_handler(lambda m: m.text.split(".")[0].isdigit())
async def surah_selected(message: types.Message):
    surah_number = int(message.text.split(".")[0])
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)

    limit = 20 if premium==1 else 5

    for i in range(1,limit+1):
        r = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{surah_number}:{i}/editions/quran-uthmani,uz.sodik"
        ).json()

        arabic = r['data'][0]['text']
        uzbek = r['data'][1]['text']
        surah = r['data'][0]['surah']['englishName']

        await message.answer(f"{surah} сураси {i}-оят\n\n{arabic}\n\n{uzbek}")

# ======================
# ARABIC ALPHABET (FULL)
# ======================

arabic_letters = [
("ب","Ба","б","بـ","بسم","ـبـ","كتاب","ـب","حب"),
("ت","Та","т","تـ","توبة","ـتـ","بيت","ـت","صوت"),
("ث","Са","с","ثـ","ثواب","ـثـ","حديث","ـث","بحث"),
]

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text=="📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("📘 Ҳарфни танланг:",reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):
    l = next(x for x in arabic_letters if x[0]==message.text)
    await message.answer(
f"""📘 Ҳарф: {l[0]}

🔤 Номи: {l[1]}
📖 Ўқилиши: {l[2]}

📌 Сўз бошида: {l[3]} → {l[4]}
📌 Сўз ўртасида: {l[5]} → {l[6]}
📌 Сўз охирида: {l[7]} → {l[8]}
""", reply_markup=alphabet_keyboard())

# ======================
# STATISTICS
# ======================

@dp.message_handler(lambda m: m.text=="📊 Статистика")
async def stats(message: types.Message):
    ayah,premium,score = get_user(message.from_user.id)
    await message.answer(
        f"📖 Оят индекси: {ayah}\n⭐ Балл: {score}\n💎 Premium: {'Ҳа' if premium else 'Йўқ'}"
    )

# ======================
# GRAMMAR (WORKING BASE)
# ======================

def grammar_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    kb.add(
        "1️⃣ Ҳаракатлар","2️⃣ Танвин",
        "3️⃣ Сукун ва Шадда","4️⃣ Исм",
        "5️⃣ Феъл","6️⃣ Ҳарф",
        "7️⃣ Жумла турлари","8️⃣ Иъроб",
        "🏠 Бош меню"
    )
    return kb

@dp.message_handler(lambda m: m.text=="📚 Грамматика")
async def grammar_menu(message: types.Message):
    await message.answer("📚 Грамматика бўлими:",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("1️⃣"))
async def g1(message: types.Message):
    await message.answer("Фатҳа, Касра, Дамма",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("2️⃣"))
async def g2(message: types.Message):
    await message.answer("Танвин: ً ٍ ٌ",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("3️⃣"))
async def g3(message: types.Message):
    await message.answer("Сукун ва Шадда",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("4️⃣"))
async def g4(message: types.Message):
    await message.answer("Исм турлари",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("5️⃣"))
async def g5(message: types.Message):
    await message.answer("Феъл турлари",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("6️⃣"))
async def g6(message: types.Message):
    await message.answer("Ҳарфлар",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("7️⃣"))
async def g7(message: types.Message):
    await message.answer("Жумла турлари",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text.startswith("8️⃣"))
async def g8(message: types.Message):
    await message.answer("Иъроб",reply_markup=grammar_keyboard())

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
