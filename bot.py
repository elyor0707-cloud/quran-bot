import requests
import os
import sqlite3
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from openai import OpenAI
import difflib

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI(api_key=OPENAI_API_KEY)

recitation_mode = {}

# ======================
# QIROAT MODE START
# ======================

@dp.message_handler(lambda m: m.text=="🎙 Қироат текшириш")
async def start_recitation(message: types.Message):
    recitation_mode[message.from_user.id] = True
    await message.answer("🎙 Илтимос, ўқимоқчи бўлган оятингизни овоз орқали юборинг.")


# ======================
# VOICE HANDLER
# ======================

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):

    if message.from_user.id not in recitation_mode:
        return

    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    downloaded = await bot.download_file(file_path)

    with open("voice.ogg","wb") as f:
        f.write(downloaded.read())

    # Whisper STT
    audio_file = open("voice.ogg","rb")

    transcript = ai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ar"
    )

    spoken_text = transcript.text.strip()

    # Текшириш учун охирги кўрилган оят
    ayah_index,_ = get_user(message.from_user.id)

    r = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{ayah_index}/quran-uthmani"
    ).json()

    correct_text = r['data']['text']

    # Similarity
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

        sura = str(r['data'][0]['surah']['number']).zfill(3)
        ayah_num = str(ayah_no).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        await message.answer(
            f"{surah} сураси {ayah_no}-оят\n\n{arabic}\n\n{uzbek}",
            reply_markup=ayah_keyboard()
        )

        await message.answer_audio(audio_url)

    except:
        await message.answer("⚠️ Хатолик.")

@dp.message_handler(lambda m: m.text=="📖 Бугунги оят")
async def today_ayah(message: types.Message):
    ayah_index,score = get_user(message.from_user.id)
    await send_ayah(message,ayah_index)

@dp.message_handler(lambda m: m.text=="➡️ Кейинги")
async def next_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,score = get_user(user_id)
    ayah_index += 1
    if ayah_index>6236:
        ayah_index=1
    update_progress(user_id,ayah_index)
    await send_ayah(message,ayah_index)

@dp.message_handler(lambda m: m.text=="⬅️ Олдинги")
async def prev_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,score = get_user(user_id)
    ayah_index -= 1
    if ayah_index<1:
        ayah_index=6236
    update_progress(user_id,ayah_index)
    await send_ayah(message,ayah_index)

# ======================
# AYAH SEARCH
# ======================

search_mode = {}

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
# ARABIC ALPHABET
# ======================

arabic_letters = [
("ا","Алиф","а","ا","ـا","ـا","الله"),
("ب","Ба","б","بـ","ـبـ","ـب","بسم / كتاب / حب"),
("ت","Та","т","تـ","ـتـ","ـت","توبة / بيت / بنت"),
("ث","Са","с","ثـ","ـثـ","ـث","ثواب / مثلث / حرث"),
("ج","Жим","ж","جـ","ـجـ","ـج","جنة / رجل / خروج"),
("ح","Ҳа","ҳ","حـ","ـحـ","ـح","حق / محمد / فلاح"),
("خ","Хо","х","خـ","ـخـ","ـخ","خلق / بخيل / شيخ"),
("د","Дал","д","د","ـد","ـد","دين / عدد"),
("ذ","Зал","з","ذ","ـذ","ـذ","ذكر / هذا"),
("ر","Ро","р","ر","ـر","ـر","رحمن / بر"),
("ز","Зай","з","ز","ـز","ـز","زكاة / ميزان"),
("س","Син","с","سـ","ـسـ","ـس","سلام / مسجد / درس"),
("ش","Шин","ш","شـ","ـشـ","ـش","شمس / بشر / عرش"),
("ص","Сод","с","صـ","ـصـ","ـص","صلاة / بصير / نقص"),
("ض","Дод","д","ضـ","ـضـ","ـض","ضوء / غضب / أرض"),
("ط","То","т","طـ","ـطـ","ـط","طاعة / مطر / خط"),
("ظ","Зо","з","ظـ","ـظـ","ـظ","ظلم / منظر / حفظ"),
("ع","Айн","ъ","عـ","ـعـ","ـع","علم / بعير / سمع"),
("غ","Ғайн","ғ","غـ","ـغـ","ـغ","غفور / مغرب / بلاغ"),
("ف","Фа","ф","فـ","ـفـ","ـف","فجر / سفر / عف"),
("ق","Қоф","қ","قـ","ـقـ","ـق","قرآن / بقي / حق"),
("ك","Каф","к","كـ","ـكـ","ـك","كتاب / مكتب / ملك"),
("ل","Лам","л","لـ","ـلـ","ـل","الله / علم / أهل"),
("م","Мим","м","مـ","ـمـ","ـم","ملك / محمد / علم"),
("ن","Нун","н","نـ","ـنـ","ـن","نور / بني / سن"),
("ه","Ҳа","ҳ","هـ","ـهـ","ـه","هدى / ذهب / وجه"),
("و","Вов","в","و","ـو","ـو","وعد / نور"),
("ي","Йа","й","يـ","ـيـ","ـي","يوم / بيت / علي"),
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
    l = next(x for x in arabic_letters if x[0]==message.text)
    await message.answer(
f"""📘 Ҳарф: {l[0]}

🔤 Номи: {l[1]}
📖 Ўқилиши: {l[2]}

📌 Сўз бошида: {l[3]}
📌 Сўз ўртасида: {l[4]}
📌 Сўз охирида: {l[5]}

🕌 Мисол: {l[6]}""",reply_markup=alphabet_keyboard())

# ======================
# TEST MODE
# ======================

tests={}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id]={"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    q=random.choice(arabic_letters)
    tests[message.from_user.id]["correct"]=q[2]
    tests[message.from_user.id]["count"]+=1
    await message.answer(f"{q[0]} қайси ҳарф?")

@dp.message_handler(lambda m: m.from_user.id in tests)
async def check(message: types.Message):
    user=tests[message.from_user.id]
    if message.text.lower()==user["correct"]:
        user["score"]+=1
        await message.answer("✅")
    else:
        await message.answer(f"❌ {user['correct']}")

    if user["count"]<10:
        await ask_question(message)
    else:
        add_score(message.from_user.id,user["score"]*10)
        await message.answer(f"Натижа: {user['score']}/10",reply_markup=main_keyboard)
        del tests[message.from_user.id]

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
