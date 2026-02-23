hereimport os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import arabic_reshaper
from bidi.algorithm import get_display

# ======================
# DATABASE (ichida)
# ======================

USERS = {}

SURAH_LIST = [
    {"number": i + 1, "name": name} for i, name in enumerate([
        "Fatiha","Baqara","Ali Imran","Nisa","Maida","Anam","Araf","Anfal","Tawba","Yunus",
        "Hud","Yusuf","Rad","Ibrahim","Hijr","Nahl","Isra","Kahf","Maryam","Taha",
        "Anbiya","Hajj","Muminun","Nur","Furqan","Shuara","Naml","Qasas","Ankabut","Rum",
        "Luqman","Sajda","Ahzab","Saba","Fatir","Yasin","Saffat","Sad","Zumar","Ghafir",
        "Fussilat","Shura","Zukhruf","Dukhan","Jathiya","Ahqaf","Muhammad","Fath","Hujurat","Qaf",
        "Dhariyat","Tur","Najm","Qamar","Rahman","Waqia","Hadid","Mujadila","Hashr","Mumtahana",
        "Saff","Jumuah","Munafiqun","Taghabun","Talaq","Tahrim","Mulk","Qalam","Haqqa","Maarij",
        "Nuh","Jinn","Muzzammil","Muddathir","Qiyamah","Insan","Mursalat","Naba","Naziat","Abasa",
        "Takwir","Infitar","Mutaffifin","Inshiqaq","Buruj","Tariq","Ala","Ghashiya","Fajr","Balad",
        "Shams","Layl","Duha","Sharh","Tin","Alaq","Qadr","Bayyina","Zalzala","Adiyat",
        "Qaria","Takathur","Asr","Humaza","Fil","Quraysh","Maun","Kawthar","Kafirun","Nasr",
        "Masad","Ikhlas","Falaq","Nas"
    ])
]

def get_surahs():
    return SURAH_LIST

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "user_id": user_id,
            "current_surah": 1,
            "current_ayah": 1,
            "is_premium": False,
            "last_surah": None,
            "last_ayah": None,
            "last_page": None
        }
    return USERS[user_id]

def update_user(user_id, key, value):
    user = get_user(user_id)
    user[key] = value
    USERS[user_id] = user

def get_premium_users():
    return [u for u in USERS.values() if u.get("is_premium", False)]

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

SURAH_CACHE = {}
ALLOWED_USERS = [444536792]  # Sen va ruxsat bergan user ID lar

def check_access(user_id):
    user = get_user(user_id)
    return user.get("is_premium", False) or user_id in ALLOWED_USERS

# ======================
# MAIN MENU
# ======================

def main_menu(user_id=None):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📖 Qur'on Tilovati", callback_data="tilovat"),
        InlineKeyboardButton("🎧 Professional Qiroat", callback_data="zam_menu")
    )
    kb.row(
        InlineKeyboardButton("🌍 AI Multi-Tarjima", callback_data="ai_translate"),
        InlineKeyboardButton("📜 Fatvo & Hadis AI", callback_data="zikir_ai")
    )
    kb.row(
        InlineKeyboardButton("📚 Tajvidli Mus'haf PDF", callback_data="quron_read")
    )
    if user_id and check_access(user_id):
        kb.row(
            InlineKeyboardButton("🌍 AI Kengaytirilgan Tarjima", callback_data="ai_premium_translate"),
            InlineKeyboardButton("🎙 Maxsus Qorilar", callback_data="premium_qori"),
            InlineKeyboardButton("📚 Tajvidli Mus'haf (Premium)", callback_data="premium_pdf")
        )
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if not check_access(message.from_user.id):
        await message.answer("❌ Sizga ruxsat berilmagan.")
        return

    get_user(message.from_user.id)
    text = (
        "🕌 *QUR’ON INTELLECT PLATFORM*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 Tilovat & Tafakkur\n"
        "🎧 Qiroat & Audio\n"
        "🌍 AI Tarjima Markazi\n"
        "📜 Fatvo va Dalil AI\n"
        "📚 Tajvidli Mus'haf\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "_Ilm • Tafakkur • Amal_"
    )
    await message.answer(text, reply_markup=main_menu(message.from_user.id), parse_mode="Markdown")

# ======================
# SURAH CACHE
# ======================

async def load_surah(surah_number):
    if surah_number in SURAH_CACHE:
        return SURAH_CACHE[surah_number]
    try:
        async with session.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/quran-uthmani", timeout=10
        ) as resp:
            r = await resp.json()
            ayahs = r['data']['ayahs']
            SURAH_CACHE[surah_number] = ayahs
            return ayahs
    except Exception as e:
        print("Xato:", e)
        return None

async def send_ayah(user_id, message):
    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    ayahs = await load_surah(surah)
    if not ayahs:
        await message.answer("❌ Surani yuklab bo‘lmadi.")
        return

    data = ayahs[ayah - 1]
    arabic_text = data['text']
    surah_name = data['surah']['englishName']
    total_ayahs = data['surah']['numberOfAyahs']

    reshaped_text = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped_text)
    translit = transliterate(arabic_text)

    await message.answer(
        f"📖 *{surah_name} surasi | {ayah}-oyat*\n\n{bidi_text}\n\n_{translit}_",
        parse_mode="Markdown"
    )

    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)
    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

    kb_audio = InlineKeyboardMarkup(row_width=3)
    if ayah > 1:
        kb_audio.insert(InlineKeyboardButton("⬅ Oldingi", callback_data="prev"))
    kb_audio.insert(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    if ayah < total_ayahs:
        kb_audio.insert(InlineKeyboardButton("➡ Keyingi", callback_data="next"))
    await message.answer_audio(audio=audio_url, reply_markup=kb_audio)

def transliterate(arabic_text):
    rules = {
        "ب": "b", "س": "s", "م": "m", "ا": "a",
        "ل": "l", "ه": "h", "ر": "r", "ح": "h",
        "ن": "n", "ي": "y", "ق": "q", "د": "d"
    }
    result = ""
    for ch in arabic_text:
        result += rules.get(ch, ch)
    return result

# ======================
# PREMIUM HANDLERS
# ======================

@dp.callback_query_handler(lambda c: c.data == "ai_premium_translate")
async def ai_premium_translate(callback: types.CallbackQuery):
    if not check_access(callback.from_user.id):
        await callback.answer("❌ Premium foydalanuvchilar uchun.")
        return
    await callback.message.edit_text(
        "🌍 Premium AI Tarjima rejimi.\n\n"
        "Matn yuboring, biz uni kengaytirilgan tarjima qilamiz."

)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "premium_pdf")
async def premium_pdf(callback: types.CallbackQuery):
    if not check_access(callback.from_user.id):
        await callback.answer("❌ Premium foydalanuvchilar uchun.")
        return
    # Faylni o'zing yuklab qo'yasan (tajvidli_mushaf.pdf)
    await callback.message.answer_document(
        open("tajvidli_mushaf.pdf", "rb"),
        caption="📚 Tajvidli Mus'haf PDF (Premium)"
    )
    await callback.answer()

PREMIUM_RECITERS = [
    ("🎙 Shayx Alijon (Premium)", "Alijon_Qori_128kbps"),
    ("🎙 Maxsus Qori 2", "Special_Qori_128kbps")
]

@dp.callback_query_handler(lambda c: c.data == "premium_qori")
async def premium_qori(callback: types.CallbackQuery):
    if not check_access(callback.from_user.id):
        await callback.answer("❌ Premium foydalanuvchilar uchun.")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    for name, reciter in PREMIUM_RECITERS:
        kb.add(InlineKeyboardButton(name, callback_data=f"qori|{reciter}"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    await callback.message.edit_text("🎧 Premium Qorilar\n\nQorini tanlang:", reply_markup=kb)
    await callback.answer()

# ======================
# ADMIN COMMANDS
# ======================

@dp.message_handler(commands=['addpremium'])
async def add_premium_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("❌ Siz admin emassiz.")
        return
    try:
        user_id = int(message.get_args())
        update_user(user_id, "is_premium", True)
        await message.answer(f"✅ Foydalanuvchi {user_id} premiumga qo‘shildi.")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

@dp.message_handler(commands=['delpremium'])
async def del_premium_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("❌ Siz admin emassiz.")
        return
    try:
        user_id = int(message.get_args())
        update_user(user_id, "is_premium", False)
        await message.answer(f"✅ Foydalanuvchi {user_id} premiumdan olib tashlandi.")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

@dp.message_handler(commands=['listpremium'])
async def list_premium_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("❌ Siz admin emassiz.")
        return
    try:
        premium_users = get_premium_users()
        if not premium_users:
            await message.answer("📭 Premium foydalanuvchilar yo‘q.")
        else:
            text = "👑 Premium foydalanuvchilar:\n\n"
            text += "\n".join([str(u["user_id"]) for u in premium_users])
            await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

# ======================
# MENU HANDLER
# ======================

@dp.callback_query_handler(lambda c: c.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🕌 *QUR’ON INTELLECT PLATFORM*",
        reply_markup=main_menu(callback.from_user.id),
        parse_mode="Markdown"
    )
    await callback.answer()

# ======================
# STARTUP / SHUTDOWN
# ======================

async def on_startup(dp):
    global session
    session = aiohttp.ClientSession()
    print("✅ Bot ishga tushdi")

async def on_shutdown(dp):
    await session.close()

if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    ) 
