import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_surahs, get_user, update_user
import arabic_reshaper
from bidi.algorithm import get_display

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

SURAH_CACHE = {}
USER_QORI = {}
ALLOWED_USERS = [123456789]  # Sen va ruxsat bergan user ID lar

def check_access(user_id):
    return user_id in ALLOWED_USERS

# ======================
# MAIN MENU
# ======================

def main_menu():
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
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")

# ======================
# QURON TILOVATI
# ======================

@dp.callback_query_handler(lambda c: c.data == "tilovat")
async def tilovat_menu(callback: types.CallbackQuery):
    surahs = get_surahs()
    kb = InlineKeyboardMarkup(row_width=4)
    for surah in surahs:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}-{surah['name']}",
                callback_data=f"surah_{surah['number']}"
            )
        )
    kb.row(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    await callback.message.edit_text("📖 Surani tanlang:", reply_markup=kb)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):
    surah_id = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_surah", surah_id)
    update_user(callback.from_user.id, "current_ayah", 1)
    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()

# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):
    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    loading = await message.answer("⏳ Yuklanmoqda...")
    async with session.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani"
    ) as resp:
        r = await resp.json()

    arabic_text = r['data'][0]['text']
    surah_name = r['data'][0]['surah']['englishName']
    total_ayahs = r['data'][0]['surah']['numberOfAyahs']

    reshaped_text = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped_text)
    translit = transliterate(arabic_text)

    await loading.delete()
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
    # Arabcha harflarni lotincha o‘qilishi qoidalari
    return "Lotincha o‘qilishi (demo)"

# ======================
# NAVIGATION
# ======================

@dp.callback_query_handler(lambda c: c.data in ["next", "prev"])
async def navigation(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    if surah not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah] = r['data']['numberOfAyahs']

    total_ayahs = SURAH_CACHE[surah]
    if callback.data == "next" and ayah < total_ayahs:
        update_user(user_id, "current_ayah", ayah + 1)
    elif callback.data == "prev" and ayah > 1:
        update_user(user_id, "current_ayah", ayah - 1)

    await send_ayah(user_id, callback.message)
    await callback.answer()

# ======================
# PROFESSIONAL QIROAT
# ======================

RECITERS = [
    ("🎙 Mishary Alafasy", "Alafasy_128kbps"),
    ("🎙 Abdul Rahman Sudais", "Sudais_128kbps"),
    ("🎙 Saad Al-Ghamdi", "Ghamdi_128kbps"),
    ("🎙 Minshawi", "Minshawi_128kbps"),
    ("🎙 Shayx Alijon", "Alijon_Qori_128kbps"),
]

@dp.callback_query_handler(lambda c: c.data == "zam_menu")
async def zam_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    for name, reciter in RECITERS:
        kb.add(InlineKeyboardButton(name, callback_data=f"qori|{reciter}"))
    kb.add(InlineKeyboardButton("🔎 Qidiruv", callback_data="search_qiroat"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    await callback.message.edit_text("🎧 Professional Qiroat\n\nQorini tanlang:", reply_markup=kb)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("qori|"))
async def qori_surah_list(callback: types.CallbackQuery):
    _, reciter = callback.data.split("|")
    async with session.get("https://api.alquran.cloud/v1/surah") as resp:
        data = await resp.json()
    surahs = data["data"]

    kb = InlineKeyboardMarkup(row_width=4)
    for surah in surahs:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}-{surah['englishName']}",
                callback_data=f"play|{reciter}|{surah['number']}"
            )
        )
    kb.row(
        InlineKeyboardButton("🎙 Qorilar", callback_data="zam_menu"),
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
    )
    await callback.message.edit_text("📖 Surani tanlang:", reply_markup=kb)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("play|"))
async def play_surah(callback: types.CallbackQuery):
    await callback.answer("⏳ Yuklanmoqda...")
    _, reciter, surah_id = callback.data.split("|")
    surah_id = int(surah_id)
    sura = str(surah_id).zfill(3)

    async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_id}") as resp:
        data = await resp.json()
    total_ayahs = data
    total_ayahs = data["data"]["numberOfAyahs"]

    for ayah in range(1, total_ayahs + 1):
        ayah_str = str(ayah).zfill(3)
        audio_url = f"https://everyayah.com/data/{reciter}/{sura}{ayah_str}.mp3"
        await callback.message.answer_audio(audio=audio_url)

# ======================
# QIROAT QIDIRUV
# ======================

@dp.callback_query_handler(lambda c: c.data == "search_qiroat")
async def search_qiroat(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔎 Qiroat qidiruv rejimi.\n\n"
        "Format: `qiroat <reciter> <surah>:<start>-<end>`\n"
        "Masalan: `qiroat Alafasy_128kbps 2:1-200`",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message_handler(lambda m: m.text.startswith("qiroat "))
async def qiroat_search(message: types.Message):
    try:
        _, reciter, range_str = message.text.split(" ", 2)
        surah_id, ayah_range = range_str.split(":")
        surah_id = int(surah_id)
        start, end = map(int, ayah_range.split("-"))

        sura = str(surah_id).zfill(3)
        for ayah in range(start, end + 1):
            ayah_str = str(ayah).zfill(3)
            audio_url = f"https://everyayah.com/data/{reciter}/{sura}{ayah_str}.mp3"
            await message.answer_audio(audio=audio_url)

    except Exception as e:
        await message.answer(f"❌ Xato format: {e}")

# ======================
# MENU
# ======================

@dp.callback_query_handler(lambda c: c.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🕌 *QUR’ON INTELLECT PLATFORM*",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ======================
# STARTUP
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
