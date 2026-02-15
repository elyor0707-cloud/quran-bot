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
    last_active TEXT,
    badge TEXT DEFAULT 'Beginner'
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score,level,streak,last_active,badge FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id,last_active) VALUES (?,?)",
                       (user_id,str(datetime.now().date())))
        conn.commit()
        return 1,0,0,1,0,str(datetime.now().date()),"Beginner"
    return row

def update_progress(user_id, value):
    cursor.execute("UPDATE users SET ayah_progress=? WHERE user_id=?", (value, user_id))
    conn.commit()

def update_level_and_badge(user_id):
    cursor.execute("SELECT score FROM users WHERE user_id=?", (user_id,))
    score = cursor.fetchone()[0]

    level = score // 100 + 1

    if score < 200:
        badge = "🥉 Beginner"
    elif score < 500:
        badge = "🥈 Intermediate"
    elif score < 1000:
        badge = "🥇 Advanced"
    else:
        badge = "👑 Master"

    cursor.execute("UPDATE users SET level=?,badge=? WHERE user_id=?",
                   (level,badge,user_id))
    conn.commit()

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()
    update_level_and_badge(user_id)

def update_streak(user_id):
    today = str(datetime.now().date())
    cursor.execute("SELECT last_active,streak FROM users WHERE user_id=?", (user_id,))
    last, streak = cursor.fetchone()
    if last != today:
        streak += 1
        cursor.execute("UPDATE users SET streak=?,last_active=? WHERE user_id=?",
                       (streak,today,user_id))
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
    "🏆 Leaderboard",
    "🎯 Daily Challenge",
    "💎 Premium"
)

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# TEST SYSTEM (4 VARIANT)
# ======================

arabic_letters = [
("ا","а"),("ب","б"),("ت","т"),("ث","с"),("ج","ж"),
("ح","ҳ"),("خ","х"),("د","д"),("ذ","з"),("ر","р"),
("ز","з"),("س","с"),("ش","ш"),("ص","с"),("ض","д"),
("ط","т"),("ظ","з"),("ع","ъ"),("غ","ғ"),("ف","ф"),
("ق","қ"),("ك","к"),("ل","л"),("م","м"),("ن","н"),
("ه","ҳ"),("و","в"),("ي","й"),
]

tests = {}

@dp.message_handler(lambda m: m.text == "🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id] = {"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q = random.choice(arabic_letters)
    correct = q[1]

    options = [correct]
    while len(options) < 4:
        opt = random.choice(arabic_letters)[1]
        if opt not in options:
            options.append(opt)

    random.shuffle(options)

    tests[message.from_user.id]["correct"] = correct
    tests[message.from_user.id]["count"] += 1

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

    correct = user_test["correct"]
    premium = get_user(message.from_user.id)[1]

    if message.text == correct:
        xp = 20 if premium else 10
        user_test["score"] += 1
        add_score(message.from_user.id, xp)
        await message.answer(f"✅ Тўғри! +{xp} XP")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {correct}")

    if user_test["count"] < 10:
        await ask_question(message)
    else:
        final_score = user_test["score"]
        await message.answer(
            f"🏁 Тест тугади!\n\nНатижа: {final_score}/10",
            reply_markup=main_keyboard
        )
        tests.pop(message.from_user.id)

# ======================
# STATISTICS
# ======================

@dp.message_handler(lambda m: m.text == "📊 Статистика")
async def stats(message: types.Message):
    ayah,premium,score,level,streak,last,badge = get_user(message.from_user.id)
    await message.answer(f"""
📊 Сизнинг статистикангиз:

⭐ XP: {score}
📈 Level: {level}
🔥 Streak: {streak} кун
🏅 Badge: {badge}
💎 Premium: {"Ҳа" if premium==1 else "Йўқ"}
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
# DAILY CHALLENGE
# ======================

@dp.message_handler(lambda m: m.text == "🎯 Daily Challenge")
async def daily_challenge(message: types.Message):
    q = random.choice(arabic_letters)
    await message.answer(f"🎯 Бугунги савол:\nБу қайси ҳарф?\n\n{q[0]}")

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text == "💎 Premium")
async def premium(message: types.Message):
    await message.answer("""
💎 Premium:

✔ XP ×2
✔ 20 та оят/кун
✔ Сертификат
✔ Кенгайтирилган тест
""")

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
