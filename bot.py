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

# ======================
# BUGUNGI OYAT
# ======================

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)

    limit = 5 if premium==0 else 20

    for i in range(ayah_index,ayah_index+limit):
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

    update_progress(user_id,ayah_index+limit)

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

def alphabet_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🔊 Аудио", "🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("Ҳарфни танланг:", reply_markup=alphabet_keyboard())

@dp.message_handler(lambda m: m.text == "🏠 Бош меню")
async def home(message: types.Message):

    if message.from_user.id in current_letter:
        del current_letter[message.from_user.id]

    await message.answer("🏠 Бош меню", reply_markup=main_keyboard)

current_letter = {}

@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):

    letter = next(l for l in arabic_letters if l[0] == message.text)
    current_letter[message.from_user.id] = letter

    await message.answer(
        f"""
📘 Ҳарф: {letter[0]}

🔤 Номи: {letter[1]}
📖 Ўқилиши: {letter[2]}

📌 Бошида: {letter[3]}
📌 Ўртасида: {letter[4]}
📌 Охирида: {letter[5]}

🕌 Мисол: {letter[6]}
""",
        reply_markup=alphabet_keyboard()  # ← ЭНГ МУҲИМИ ШУ
    )


@dp.message_handler(lambda m: m.text == "🔊 Аудио")
async def letter_audio(message: types.Message):

    if message.from_user.id not in current_letter:
        await message.answer("Аввал ҳарф танланг.", reply_markup=alphabet_keyboard())
        return

    letter = current_letter[message.from_user.id]

    await message.answer(f"🔊 Талаффуз: {letter[2]}", reply_markup=alphabet_keyboard())


# ======================
# GRAMMAR (FULL MODULE)
# ======================

@dp.message_handler(lambda m: m.text=="📚 Грамматика")
async def grammar(message: types.Message):

    text = """
📚 АРАБ ГРАММАТИКАСИ ТЎЛИҚ ҚЎЛЛАНМА

1️⃣ Ҳаракатлар
َ Фатҳа
ِ Касра
ُ Дамма

2️⃣ Танвин
ً  ٍ  ٌ

3️⃣ Сукун
ْ

4️⃣ Шадда
ّ

5️⃣ Мадд ҳарфлари
ا  و  ي

6️⃣ Исм
7️⃣ Феъл
8️⃣ Ҳарф
9️⃣ Жумла турлари
10️⃣ Эркак / Аёл шакллари
11️⃣ Жамлик
12️⃣ Замонлар
13️⃣ Иъроб асослари
14️⃣ Муфрад / Мусанно / Жамъ
15️⃣ Тақдирий ҳаракатлар
"""

    await message.answer(text)

# ======================
# TEST SYSTEM
# ======================

tests = {}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id]={"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q = random.choice(arabic_letters)
    tests[message.from_user.id]["correct"]=q[2]
    tests[message.from_user.id]["count"]+=1

    kb=ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("❌ Тестни тугатиш","🏠 Бош меню")

    await message.answer(
        f"{tests[message.from_user.id]['count']}/10\nБу қайси ҳарф?\n\n{q[0]}",
        reply_markup=kb
    )

@dp.message_handler(lambda m: m.text=="❌ Тестни тугатиш")
async def stop_test(message: types.Message):
    if message.from_user.id in tests:
        del tests[message.from_user.id]
    await message.answer("Тест тўхтатилди",reply_markup=main_keyboard)

@dp.message_handler(lambda m: m.from_user.id in tests and m.text not in ["❌ Тестни тугатиш","🏠 Бош меню"])
async def check_answer(message: types.Message):

    user_test = tests[message.from_user.id]

    if message.text.lower()==user_test["correct"]:
        user_test["score"]+=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user_test['correct']}")

    if user_test["count"]<10:
        await ask_question(message)
    else:
        final_score=user_test["score"]
        add_score(message.from_user.id,final_score*10)

        await message.answer(
            f"🏁 Тест тугади!\n\nНатижа: {final_score}/10\nБалл: {final_score*10}",
            reply_markup=main_keyboard
        )

        del tests[message.from_user.id]

# ======================
# STATISTICS
# ======================

@dp.message_handler(lambda m: m.text=="📊 Статистика")
async def stats(message: types.Message):
    ayah,premium,score = get_user(message.from_user.id)

    await message.answer(f"""
📊 СТАТИСТИКА

📖 Оят индекси: {ayah}
⭐ Балл: {score}
💎 Premium: {"Ҳа" if premium==1 else "Йўқ"}
""")

# ======================
# LEADERBOARD
# ======================

@dp.message_handler(lambda m: m.text=="🏆 Leaderboard")
async def leaderboard(message: types.Message):
    cursor.execute("SELECT user_id,score FROM users ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    text="🏆 ТОП 10\n\n"
    for i,row in enumerate(rows,1):
        text+=f"{i}. {row[0]} — {row[1]} XP\n"

    await message.answer(text)

# ======================
# PREMIUM
# ======================

@dp.message_handler(lambda m: m.text=="💎 Premium")
async def premium(message: types.Message):
    await message.answer("""
💎 Premium:

✔ 20 та оят/кун
✔ XP ×2
✔ Кенгайтирилган тест
✔ Сертификат
""")

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
