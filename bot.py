from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import requests

async def send_ayah(message, surah, ayah):
    r = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,uz.sodik"
    ).json()

    arabic = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']

    text = f"""
📖 {surah_name} сураси
Оят: {ayah}

{arabic}

{uzbek}
"""

    await message.answer(text)

    # AUDIO
    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)

    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

    await message.answer_audio(audio_url)

from database import get_surahs, get_user, update_user, get_ayah

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# SURAH LIST
# ======================

def surah_keyboard():
    kb = InlineKeyboardMarkup(row_width=4)
    surahs = get_surahs()

    for surah in surahs:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}. {surah['name']}",
                callback_data=f"surah_{surah['number']}"
            )
        )

    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("📖 Сурани танланг:", reply_markup=surah_keyboard())

# ======================
# SURAH SELECT
# ======================

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):

    surah_number = int(callback.data.split("_")[1])

    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)

    await send_ayah(callback.message, surah, ayah)
    await callback.answer()

# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):

    user = get_user(user_id)

    surah = user["current_surah"]
    ayah = user["current_ayah"]

    data = get_ayah(surah, ayah)

    text = f"""
📖 {data['surah_name']}
Оят: {ayah}

{data['arabic']}

{data['uzbek']}
"""

    kb = InlineKeyboardMarkup()

    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Олдинги", callback_data="prev"))

    if ayah < data["total_ayahs"]:
        kb.insert(InlineKeyboardButton("➡ Кейинги", callback_data="next"))

    kb.add(InlineKeyboardButton("🏠 Бош меню", callback_data="menu"))

    await message.answer(text, reply_markup=kb)

# ======================
# NAVIGATION
# ======================

@dp.callback_query_handler(lambda c: c.data in ["next", "prev", "menu"])
async def navigation(callback: types.CallbackQuery):

    user_id = callback.from_user.id
    user = get_user(user_id)

    surah = user["current_surah"]
    ayah = user["current_ayah"]

    if callback.data == "next":
        update_user(user_id, "current_ayah", ayah + 1)

    elif callback.data == "prev":
        update_user(user_id, "current_ayah", ayah - 1)

    elif callback.data == "menu":
        await callback.message.answer(
            "📖 Сурани танланг:",
            reply_markup=surah_keyboard()
        )
        await callback.answer()
        return

    await send_ayah(user_id, callback.message)
    await callback.answer()

# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
