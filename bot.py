import requests
import os
import sqlite3
import random
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
    level INTEGER DEFAULT 1,
    streak INTEGER DEFAULT 0,
    last_active TEXT
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score,level,streak,last_active FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        today = str(datetime.now().date())
        cursor.execute("INSERT INTO users (user_id,last_active) VALUES (?,?)",(user_id,today))
        conn.commit()
        return 1,0,0,1,0,today
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

# ======================
# MAIN MENU
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_keyboard.add(
    "📖 Бугунги оят",
    "📘 Араб алифбоси",
    "📚 Грамматика",
    "🏆 Leaderboard",
    "🧠 Тест режими"
)

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# BUGUNGI OYAT
# ======================

@dp.message_handler(lambda m: m.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index,premium,score,level,streak,last = get_user(user_id)

    limit = 5 if premium==0 else 20

    for i in range(ayah_index, ayah_index+limit):
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

    update_progress(user_id, ayah_index+limit)

# ======================
# ARABIC ALPHABET
# ======================

arabic_letters = [
("ا","Алиф","а","ا","ـا","ـا","اللّٰه"),
("ب","Ба","б","بـ","ـبـ","ـب","بسم"),
("ت","Та","т","تـ","ـتـ","ـت","توبة"),
("ث","Са","с","ثـ","ـثـ","ـث","ثواب"),
("ج","Жим","ж","جـ","ـجـ","ـج","جنة"),
("ح","Ҳа","ҳ","حـ","ـحـ","ـح","حق"),
("خ","Хо","х","خـ","ـخـ","ـخ","خلق"),
("د","Дал","д","د","ـد","ـد","دين"),
("ر","Ро","р","ر","ـر","ـر","رحمن"),
("م","Мим","м","مـ","ـمـ","ـم","ملك"),
("ي","Йа","й","يـ","ـيـ","ـي","يوم"),
]

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:", reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text == "🏠 Бош меню")
async def back_home(message: types.Message):
    await message.answer("Бош меню", reply_markup=main_keyboard)

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
# GRAMMAR
# ======================

@dp.message_handler(lambda m: m.text == "📚 Грамматика")
async def grammar(message: types.Message):
    await message.answer("""
📚 Араб грамматикаси:

1️⃣ Фатҳа َ  
2️⃣ Касра ِ  
3️⃣ Дамма ُ  
4️⃣ Танвин  
5️⃣ Сукун ْ  
6️⃣ Шадда ّ  
""")

# ======================
# LEADERBOARD
# ======================

@dp.message_handler(lambda m: m.text == "🏆 Leaderboard")
async def leaderboard(message: types.Message):
    cursor.execute("SELECT user_id,score FROM users ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    text="🏆 ТОП 10\n\n"
    for i,row in enumerate(rows,1):
        text+=f"{i}. {row[0]} — {row[1]} XP\n"

    await message.answer(text)

# ======================
# TEST
# ======================

tests = {}

@dp.message_handler(lambda m: m.text == "🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id] = {"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q = random.choice(arabic_letters)
    correct = q[2]

    options = [correct]
    while len(options)<4:
        opt = random.choice(arabic_letters)[2]
        if opt not in options:
            options.append(opt)

    random.shuffle(options)

    tests[message.from_user.id]["correct"]=correct
    tests[message.from_user.id]["count"]+=1

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*options)
    kb.add("❌ Тестни тугатиш","🏠 Бош меню")

    await message.answer(
        f"{tests[message.from_user.id]['count']}/10\nБу қайси ҳарф?\n\n{q[0]}",
        reply_markup=kb
    )

@dp.message_handler(lambda m: m.text == "❌ Тестни тугатиш")
async def stop_test(message: types.Message):
    tests.pop(message.from_user.id, None)
    await message.answer("Тест тўхтатилди.", reply_markup=main_keyboard)

@dp.message_handler(lambda m: m.from_user.id in tests and m.text not in ["❌ Тестни тугатиш","🏠 Бош меню"])
async def check_answer(message: types.Message):
    user_test = tests[message.from_user.id]

    if message.text == user_test["correct"]:
        user_test["score"] +=1
        add_score(message.from_user.id,10)
        await message.answer("✅ Тўғри! +10 XP")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user_test['correct']}")

    if user_test["count"]<10:
        await ask_question(message)
    else:
        final_score = user_test["score"]
        await message.answer(
            f"🏁 Тест тугади!\nНатижа: {final_score}/10",
            reply_markup=main_keyboard
        )
        tests.pop(message.from_user.id)

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
