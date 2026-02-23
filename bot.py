import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import arabic_reshaper
from bidi.algorithm import get_display

# ======================
# DATABASE (Memory)
# ======================

USERS = {}
SURAH_CACHE = {}
ALLOWED_USERS = [444536792]  # O'zingning ID

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "current_surah": 1,
            "current_ayah": 1,
            "is_premium": False,
        }
    return USERS[user_id]

def update_user(user_id, key, value):
    USERS[user_id][key] = value

def check_access(user_id):
    user = get_user(user_id)
    return user.get("is_premium", False) or user_id in ALLOWED_USERS

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

session = None

# ======================
# MENU
# ======================

def main_menu(user_id=None):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📖 Tilovat", callback_data="tilovat"),
        InlineKeyboardButton("🎧 Premium Qori", callback_data="premium_qori")
    )
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)

    text = (
        "🕌 QUR’ON BOT\n\n"
        "📖 Tilovat\n"
        "🎧 Premium Qori\n"
    )

    await message.answer(text, reply_markup=main_menu(message.from_user.id))

# ======================
# LOAD SURAH
# ======================

async def load_surah(surah_number):
    if surah_number in SURAH_CACHE:
        return SURAH_CACHE[surah_number]

    try:
        async with session.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/quran-uthmani"
        ) as resp:
            data = await resp.json()
            ayahs = data["data"]["ayahs"]
            SURAH_CACHE[surah_number] = ayahs
            return ayahs
    except Exception as e:
        print("API Xato:", e)
        return None

# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):
    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    ayahs = await load_surah(surah)
    if not ayahs:
        await message.answer("❌ Surani yuklab bo‘lmadi.")
        return

    data = ayahs[ayah - 1]
    arabic_text = data["text"]
    total = data["surah"]["numberOfAyahs"]
    surah_name = data["surah"]["englishName"]

    reshaped = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped)

    text = f"📖 {surah_name} | {ayah}-oyat\n\n{bidi_text}"

    kb = InlineKeyboardMarkup(row_width=3)
    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅", callback_data="prev"))
    kb.insert(InlineKeyboardButton("🏠", callback_data="menu"))
    if ayah < total:
        kb.insert(InlineKeyboardButton("➡", callback_data="next"))

    await message.answer(text, reply_markup=kb)

# ======================
# CALLBACKS
# ======================

@dp.callback_query_handler(lambda c: c.data == "tilovat")
async def tilovat(callback: types.CallbackQuery):
    update_user(callback.from_user.id, "current_surah", 1)
    update_user(callback.from_user.id, "current_ayah", 1)
    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "next")
async def next_ayah(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    user["current_ayah"] += 1
    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "prev")
async def prev_ayah(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user["current_ayah"] > 1:
        user["current_ayah"] -= 1
    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "premium_qori")
async def premium_qori(callback: types.CallbackQuery):
    if not check_access(callback.from_user.id):
        await callback.answer("❌ Premium emas", show_alert=True)
        return

    await callback.message.answer("🎧 Premium rejim yoqildi.")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "menu")
async def back_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🕌 QUR’ON BOT",
        reply_markup=main_menu(callback.from_user.id)
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
