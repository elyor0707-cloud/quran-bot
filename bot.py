import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from database import get_surahs, get_user, update_user
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =========================
# MAIN MENU
# =========================

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📖 Surani tanlang", callback_data="surah_menu"))
    kb.add(InlineKeyboardButton("📚 Mushaf rejimi", callback_data="mushaf"))
    kb.add(InlineKeyboardButton("🎧 Zam suralar", callback_data="zam"))
    kb.add(InlineKeyboardButton("🕌 Fatvo", callback_data="fatvo"))
    kb.add(InlineKeyboardButton("📊 Statistika", callback_data="stat"))
    return kb

# =========================
# START
# =========================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("Асосий меню:", reply_markup=main_menu())

# =========================
# STATISTIKA
# =========================

@dp.callback_query_handler(lambda c: c.data == "stat")
async def stat(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)

    text = f"""
📊 Statistika

Oxirgi sura: {user.get('last_surah')}
Oxirgi oyat: {user.get('last_ayah')}
Mushaf sahifa: {user.get('mushaf_page')}
"""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("▶ Davom etish", callback_data="continue"))

    await callback.message.answer(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "continue")
async def continue_read(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    update_user(callback.from_user.id, "current_surah", user["last_surah"])
    update_user(callback.from_user.id, "current_ayah", user["last_ayah"])
    await send_ayah(callback.from_user.id, callback.message)

# =========================
# SURAH TANLASH
# =========================

def surah_keyboard():
    kb = InlineKeyboardMarkup(row_width=4)
    for s in get_surahs():
        kb.insert(InlineKeyboardButton(
            f"{s['number']}. {s['name']}",
            callback_data=f"surah_{s['number']}"
        ))
    return kb

@dp.callback_query_handler(lambda c: c.data == "surah_menu")
async def open_surah(callback: types.CallbackQuery):
    await callback.message.answer("Sura tanlang:", reply_markup=surah_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):
    surah = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_surah", surah)
    update_user(callback.from_user.id, "current_ayah", 1)
    await send_ayah(callback.from_user.id, callback.message)

# =========================
# MUSHAF REJIMI
# =========================

@dp.callback_query_handler(lambda c: c.data == "mushaf")
async def mushaf(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    page = user.get("mushaf_page") or 1

    img_url = f"https://everyayah.com/data/quranpngs/page{str(page).zfill(3)}.png"

    await callback.message.answer_photo(img_url)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅ Oldingi", callback_data="m_prev"))
    kb.add(InlineKeyboardButton("➡ Keyingi", callback_data="m_next"))

    await callback.message.answer("Navigatsiya:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["m_prev", "m_next"])
async def mushaf_nav(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    page = user.get("mushaf_page") or 1

    if callback.data == "m_next":
        page += 1
    else:
        page = max(1, page - 1)

    update_user(callback.from_user.id, "mushaf_page", page)

    img_url = f"https://everyayah.com/data/quranpngs/page{str(page).zfill(3)}.png"
    await callback.message.answer_photo(img_url)

# =========================
# ZAM SURALAR
# =========================

@dp.callback_query_handler(lambda c: c.data == "zam")
async def zam_menu(callback: types.CallbackQuery):

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("1 minutgacha", callback_data="zam1"))
    kb.add(InlineKeyboardButton("2 minutgacha", callback_data="zam2"))
    kb.add(InlineKeyboardButton("2 minutdan ko‘p", callback_data="zam3"))

    await callback.message.answer("Tanlang:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("zam"))
async def zam_audio(callback: types.CallbackQuery):

    # MISOL AUDIO (keyin haqiqiy link bilan almashtiramiz)
    await callback.message.answer_audio(
        "https://server8.mp3quran.net/bader/001.mp3"
    )

# =========================
# FATVO
# =========================

@dp.callback_query_handler(lambda c: c.data == "fatvo")
async def fatvo_start(callback: types.CallbackQuery):
    await callback.message.answer("Savolingizni yozing:")

@dp.message_handler()
async def fatvo_search(message: types.Message):

    query = message.text

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://www.muslim.uz/index.php?searchword={query}"
        ) as resp:
            await message.answer("Natijalar topildi. Muslim.uz saytini tekshiring.")

# =========================
# SEND AYAH
# =========================

async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,uz.sodik"
        ) as resp:
            r = await resp.json()

    arabic = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']

    update_user(user_id, "last_surah", surah)
    update_user(user_id, "last_ayah", ayah)

    await message.answer(f"{arabic}\n\n{uzbek}")

# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
