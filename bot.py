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
# ARABIC ALPHABET (FULL EXTENDED)
# ======================

arabic_letters = [
("ب","Ба","б","بـ","ـبـ","ـب",
 "بسم","كتاب","حب"),
("ت","Та","т","تـ","ـتـ","ـت",
 "توبة","كتاب","بيت"),
("ج","Жим","ж","جـ","ـجـ","ـج",
 "جنة","مجلس","حج"),
]

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=6)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text=="📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:",reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):
    letter = next(l for l in arabic_letters if l[0]==message.text)

    await message.answer(f"""
📘 Ҳарф: {letter[0]}

🔤 Номи: {letter[1]}
📖 Ўқилиши: {letter[2]}

📌 Сўз бошида: {letter[3]}  → {letter[6]}
📌 Сўз ўртасида: {letter[4]}  → {letter[7]}
📌 Сўз охирида: {letter[5]}  → {letter[8]}
""",reply_markup=alphabet_keyboard())

# ======================
# FULL GRAMMAR SYSTEM
# ======================

def grammar_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    kb.add(
        "1️⃣ Ҳаракатлар",
        "2️⃣ Танвин",
        "3️⃣ Сукун ва Шадда",
        "4️⃣ Исм",
        "5️⃣ Феъл",
        "6️⃣ Ҳарф",
        "7️⃣ Жумла турлари",
        "8️⃣ Иъроб",
        "📝 Машқ режими",
        "🏠 Бош меню"
    )
    return kb

@dp.message_handler(lambda m: m.text=="📚 Грамматика")
async def grammar_menu(message: types.Message):
    await message.answer("📚 Грамматика бўлими:",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="1️⃣ Ҳаракатлар")
async def harakatlar(message: types.Message):
    await message.answer("""
📚 Ҳаракатлар

َ Фатҳа — а
ِ Касра — и
ُ Дамма — у

كَتَبَ
كُتِبَ
كِتَاب
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="2️⃣ Танвин")
async def tanvin(message: types.Message):
    await message.answer("""
📚 Танвин

ً  ٍ  ٌ

كتابٌ
كتابًا
كتابٍ
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="3️⃣ Сукун ва Шадда")
async def sukun(message: types.Message):
    await message.answer("""
📚 Сукун — ْ
📚 Шадда — ّ

مَدّ
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="4️⃣ Исм")
async def ism(message: types.Message):
    await message.answer("""
📚 Исм

كتاب
مدرسة

Муфрад / Мусанно / Жамъ
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="5️⃣ Феъл")
async def feel(message: types.Message):
    await message.answer("""
📚 Феъл

ماضي — كتب
مضارع — يكتب
أمر — اكتب
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="6️⃣ Ҳарф")
async def harf_section(message: types.Message):
    await message.answer("""
📚 Ҳарф

في
من
إلى
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="7️⃣ Жумла турлари")
async def sentence_types(message: types.Message):
    await message.answer("""
📚 Жумла турлари

جملة اسمية
الكتاب جديد

جملة فعلية
كتب الطالب
""",reply_markup=grammar_keyboard())

@dp.message_handler(lambda m: m.text=="8️⃣ Иъроб")
async def irob(message: types.Message):
    await message.answer("""
📚 Иъроб

مرفوع — ُ
منصوب — َ
مجرور — ِ
مجزوم — ْ
""",reply_markup=grammar_keyboard())

# ======================
# GRAMMAR QUIZ
# ======================

grammar_tests = {}

@dp.message_handler(lambda m: m.text=="📝 Машқ режими")
async def grammar_test_start(message: types.Message):
    grammar_tests[message.from_user.id]={"score":0,"count":0}
    await grammar_question(message)

async def grammar_question(message):
    questions=[
        ("Феъл нима?", "ҳаракат"),
        ("جمع нима?", "кўплик"),
        ("ماضي қайси замон?", "ўтган")
    ]
    q=random.choice(questions)
    grammar_tests[message.from_user.id]["correct"]=q[1]
    grammar_tests[message.from_user.id]["count"]+=1
    await message.answer(q[0])

@dp.message_handler(lambda m: m.from_user.id in grammar_tests)
async def grammar_answer(message: types.Message):
    user=grammar_tests[message.from_user.id]
    if user["correct"] in message.text.lower():
        user["score"]+=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer("❌ Нотўғри")
    if user["count"]<3:
        await grammar_question(message)
    else:
        await message.answer(f"🏁 Натижа: {user['score']}/3",reply_markup=grammar_keyboard())
        del grammar_tests[message.from_user.id]

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
