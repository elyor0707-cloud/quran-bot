import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_surahs, get_user, update_user

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
        InlineKeyboardButton("📚 Tajvidli Mus'haf PDF", callback_data="pdf")
    )

    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):

    get_user(message.from_user.id)

    text = (
        "🕌 *QUR’ON INTELLECT PLATFORM*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 Tilovat & Tafakkur\n"
        "🎧 Qiroat & Audio\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await message.answer(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

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

    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=kb
    )

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

    async with session.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani"
    ) as resp:
        r = await resp.json()

    arabic_text = r['data']['text']
    surah_name = r['data']['surah']['englishName']
    total_ayahs = r['data']['surah']['numberOfAyahs']

    await message.answer(
        f"📖 *{surah_name} surasi | {ayah}-oyat*\n\n{arabic_text}",
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

RECITER_FULL = {
    "Alafasy_128kbps": "mishaari_raashid_al_3afaasee",
    "Badr_AlTurki_128kbps": "badr_al_turki",
    "Alijon_Qori_128kbps": "alijon_qori"
}

@dp.callback_query_handler(lambda c: c.data == "zam_menu")
async def zam_menu(callback: types.CallbackQuery):

    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(InlineKeyboardButton("🎙 Mishary Alafasy", callback_data="qori|Alafasy_128kbps"))
    kb.add(InlineKeyboardButton("🎙 Badr At-Turkiy", callback_data="qori|Badr_AlTurki_128kbps"))
    kb.add(InlineKeyboardButton("🎙 Shayx Alijon", callback_data="qori|Alijon_Qori_128kbps"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))

    await callback.message.edit_text(
        "🎧 Professional Qiroat\n\nQorini tanlang:",
        reply_markup=kb
    )

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

    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=kb
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("play|"))
async def play_surah(callback: types.CallbackQuery):

    await callback.answer("⏳ Yuklanmoqda...")

    _, reciter, surah_id = callback.data.split("|")
    surah_id = int(surah_id)

    sura = str(surah_id).zfill(3)

    folder = RECITER_FULL.get(reciter)

    if not folder:
        await callback.message.answer("Qori topilmadi ❌")
        return

    full_url = f"https://download.quranicaudio.com/qdc/{folder}/{sura}.mp3"

    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🎙 Qorilar", callback_data="zam_menu"),
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
    )

    await callback.message.answer_audio(
        audio=full_url,
        caption=f"{surah_id}-sura",
        reply_markup=kb
    )

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
