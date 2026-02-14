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
# ARABIC LETTERS FULL (28)
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
("ذ","Зал","з","ذ","ـذ","ـذ","ذكر"),
("ر","Ро","р","ر","ـر","ـر","رحمن"),
("ز","Зай","з","ز","ـز","ـز","زكاة"),
("س","Син","с","سـ","ـسـ","ـس","سلام"),
("ش","Шин","ш","شـ","ـشـ","ـش","شمس"),
("ص","Сод","с","صـ","ـصـ","ـص","صلاة"),
("ض","Дод","д","ضـ","ـضـ","ـض","ضلال"),
("ط","То","т","طـ","ـطـ","ـط","طاعة"),
("ظ","Зо","з","ظـ","ـظـ","ـظ","ظلم"),
("ع","Айн","ъ","عـ","ـعـ","ـع","علم"),
("غ","Ғайн","ғ","غـ","ـغـ","ـغ","غفور"),
("ف","Фа","ф","فـ","ـفـ","ـف","فجر"),
("ق","Қоф","қ","قـ","ـقـ","ـق","قرآن"),
("ك","Каф","к","كـ","ـكـ","ـك","كتاب"),
("ل","Лам","л","لـ","ـلـ","ـل","الله"),
("م","Мим","м","مـ","ـمـ","ـم","ملك"),
("ن","Нун","н","نـ","ـنـ","ـن","نور"),
("ه","Ҳа","ҳ","هـ","ـهـ","ـه","هدى"),
("و","Вов","в","و","ـو","ـو","وعد"),
("ي","Йа","й","يـ","ـيـ","ـي","يوم"),
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
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Уйга қайтиш")
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ALPHABET
# ======================

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:", reply_markup=alphabet_table())

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

@dp.message_handler(lambda m: m.text=="🏠 Уйга қайтиш")
async def home(message: types.Message):
    await message.answer("Бош меню", reply_markup=main_keyboard)

# ======================
# TEST SYSTEM (10 QUESTIONS)
# ======================

tests = {}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id] = {"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q = random.choice(arabic_letters)
    tests[message.from_user.id]["correct"] = q[2]
    tests[message.from_user.id]["count"] += 1
    await message.answer(f"{tests[message.from_user.id]['count']}/10\nБу қайси ҳарф?\n\n{q[0]}")

@dp.message_handler(lambda m: m.from_user.id in tests)
async def check_answer(message: types.Message):
    user_test = tests[message.from_user.id]
    if message.text.lower()==user_test["correct"]:
        user_test["score"] +=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user_test['correct']}")
    if user_test["count"]<10:
        await ask_question(message)
    else:
        final_score = user_test["score"]
        add_score(message.from_user.id, final_score*10)
        await message.answer(f"""
🏁 Тест тугади!

Натижа: {final_score}/10
Балл қўшилди: {final_score*10}
""")
        del tests[message.from_user.id]

# ======================
# TODAY AYAH
# ======================

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):

    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)
    limit = 5 if premium==0 else 20

    for i in range(ayah_index, ayah_index+limit):
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

    update_progress(user_id, ayah_index+limit)

# ======================
# GRAMMAR
# ======================

@dp.message_handler(lambda m: m.text=="📚 Грамматика")
async def grammar(message: types.Message):
    await message.answer("""
📚 Араб грамматикаси:

1️⃣ Ҳаракатлар (фатҳа, касра, дамма)
2️⃣ Танвин
3️⃣ Сукун
4️⃣ Шадда
5️⃣ Исм ва феъл фарқи
6️⃣ Жумла тузилиши
""")

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text=="💎 Premium")
async def premium_info(message: types.Message):
    await message.answer("""
💎 Premium режа:

✔ 20 та оят/кун
✔ Чуқур тест
✔ Сертификат
✔ Прогресс аналитика

💳 Нархи: 20–30 USD

Тўлов учун админга мурожаат қилинг.
""")
    activate_premium(message.from_user.id)

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
