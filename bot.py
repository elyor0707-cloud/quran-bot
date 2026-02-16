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
    "📖 Бугунги оят","🔎 Оят қидириш",
    "📘 Араб алифбоси", "📊 Статистика",
    "📚 Грамматика", "🧠 Тест режими",
    "🏆 Leaderboard", "💎 Premium" )

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!",reply_markup=main_keyboard)

@dp.message_handler(lambda m: m.text=="🏠 Бош меню")
async def home(message: types.Message):
    await message.answer("🏠 Бош меню",reply_markup=main_keyboard)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ======================
# SURAH SYSTEM 114 + PAGINATION
# ======================

def get_all_surahs():
    r = requests.get("https://api.alquran.cloud/v1/surah").json()
    return r["data"]

all_surahs = get_all_surahs()


def surah_inline_keyboard(page=0):
    kb = InlineKeyboardMarkup(row_width=2)
    start = page * 10
    end = start + 10

    for surah in all_surahs[start:end]:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}. {surah['englishName']}",
                callback_data=f"surah_{surah['number']}"
            )
        )

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}")
        )
    if end < len(all_surahs):
        nav.append(
            InlineKeyboardButton("➡️", callback_data=f"page_{page+1}")
        )

    if nav:
        kb.row(*nav)

    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def change_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(
        reply_markup=surah_inline_keyboard(page)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def send_surah(callback: types.CallbackQuery):

    surah_number = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    ayah_index,premium,score = get_user(user_id)

    limit = 20 if premium==1 else 5

    for i in range(1, limit+1):

        r = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{surah_number}:{i}/editions/quran-uthmani,uz.sodik"
        ).json()

        arabic = r['data'][0]['text']
        uzbek = r['data'][1]['text']
        surah_name = r['data'][0]['surah']['englishName']

        # 📌 ТАФСИР СТИЛЬ ФОРМАТ
        text = f"""
{surah_name} сураси {i}-оят

{arabic}

{uzbek}

(Қисқача тафсир: Бу оят Аллоҳнинг раҳмати ва ҳикматини англатади.)
"""

        await callback.message.answer(text)

        # 🎧 AUDIO
        sura = str(surah_number).zfill(3)
        ayah_num = str(i).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        await callback.message.answer_audio(audio_url)

    await callback.answer()

# ======================
# AYAH SEARCH SYSTEM
# ======================

search_mode = {}

@dp.message_handler(lambda m: m.text=="🔎 Оят қидириш")
async def search_start(message: types.Message):
    search_mode[message.from_user.id] = True
    await message.answer("🔎 Қидириш учун калит сўз киритинг:")


@dp.message_handler(lambda m: m.from_user.id in search_mode)
async def search_ayah(message: types.Message):

    user_id = message.from_user.id
    keyword = message.text

    ayah_index,premium,score = get_user(user_id)

    limit = 10 if premium==1 else 3

    response = requests.get(
        f"https://api.alquran.cloud/v1/search/{keyword}/all/uz.sodik"
    ).json()

    if response["data"]["count"] == 0:
        await message.answer("❌ Натижа топилмади.")
        del search_mode[user_id]
        return

    results = response["data"]["matches"][:limit]

    for ayah in results:

        surah_name = ayah["surah"]["englishName"]
        ayah_number = ayah["numberInSurah"]

        arabic_resp = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{ayah['number']}/quran-uthmani"
        ).json()

        arabic_text = arabic_resp["data"]["text"]
        uzbek_text = ayah["text"]

        text = f"""
{surah_name} сураси {ayah_number}-оят

{arabic_text}

{uzbek_text}
"""

        await message.answer(text)

        # 🎧 AUDIO
        sura = str(ayah["surah"]["number"]).zfill(3)
        ayah_num = str(ayah_number).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        await message.answer_audio(audio_url)

    del search_mode[user_id]

# ======================
# ARABIC ALPHABET (FIXED FULL VERSION)
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
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=7)
    kb.add(*[l[0] for l in arabic_letters])
    kb.add("🏠 Бош меню")
    return kb

@dp.message_handler(lambda m: m.text=="📘 Араб алифбоси")
async def alphabet_menu(message: types.Message):
    await message.answer("📘 Ҳарфни танланг:", reply_markup=alphabet_keyboard())


@dp.message_handler(lambda m: m.text in [l[0] for l in arabic_letters])
async def letter_info(message: types.Message):
    letter = next(l for l in arabic_letters if l[0]==message.text)

    await message.answer(f"""
📘 Ҳарф: {letter[0]}

🔤 Номи: {letter[1]}
📖 Ўқилиши: {letter[2]}

📌 Сўз бошида: {letter[3]}
📌 Сўз ўртасида: {letter[4]}
📌 Сўз охирида: {letter[5]}

🕌 Мисол: {letter[6]}
""", reply_markup=alphabet_keyboard())


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
# BUGUNGI OYAT NAVIGATION SYSTEM
# ======================

def ayah_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    kb.add("⬅️ Олдинги оят","➡️ Кейинги оят")
    kb.add("🏠 Бош меню")
    return kb


async def send_ayah(message, ayah_number):

    try:
        response = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{ayah_number}/editions/quran-uthmani,uz.sodik"
        )

        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']
        surah = data['data'][0]['surah']['englishName']
        ayah_no = data['data'][0]['numberInSurah']

        sura = str(data['data'][0]['surah']['number']).zfill(3)
        ayah_num = str(ayah_no).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        await message.answer(
            f"{surah} сураси {ayah_no}-оят\n\n{arabic}\n\n{uzbek}",
            reply_markup=ayah_keyboard()
        )

        await message.answer_audio(audio_url)

    except:
        await message.answer("⚠️ Оят топилмади ёки API хатолик.")


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
    if ayah_index > 6236:
        ayah_index = 1

    update_progress(user_id,ayah_index)

    await send_ayah(message,ayah_index)


@dp.message_handler(lambda m: m.text=="⬅️ Олдинги оят")
async def prev_ayah(message: types.Message):
    user_id = message.from_user.id
    ayah_index,premium,score = get_user(user_id)

    if ayah_index > 1:
        ayah_index -= 1
    else:
        ayah_index = 6236

    update_progress(user_id,ayah_index)

    await send_ayah(message,ayah_index)

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp,skip_updates=True)
