import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import arabic_reshaper
from bidi.algorithm import get_display

USERS = {}
SURAH_CACHE = {}
ALLOWED_USERS = [444536792]
session = None  # GLOBAL SESSION

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "user_id": user_id,
            "current_surah": 1,
            "current_ayah": 1,
            "is_premium": False
        }
    return USERS[user_id]

def update_user(user_id, key, value):
    user = get_user(user_id)
    user[key] = value
    USERS[user_id] = user

def get_premium_users():
    return [u for u in USERS.values() if u.get("is_premium", False)]

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def check_access(user_id):
    user = get_user(user_id)
    return user.get("is_premium", False) or user_id in ALLOWED_USERS

def main_menu(user_id=None):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(InlineKeyboardButton("📖 Qur'on Tilovati", callback_data="tilovat"))
    if user_id and check_access(user_id):
        kb.row(InlineKeyboardButton("🌍 AI Premium Tarjima", callback_data="ai_premium_translate"))
    return kb

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("🕌 Qur’on bot ishga tushdi!", reply_markup=main_menu(message.from_user.id))

async def load_surah(surah_number):
    if surah_number in SURAH_CACHE:
        return SURAH_CACHE[surah_number]
    try:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_number}/quran-uthmani", timeout=10) as resp:
            r = await resp.json()
            ayahs = r['data']['ayahs']
            SURAH_CACHE[surah_number] = ayahs
            return ayahs
    except asyncio.TimeoutError:
        print("⏳ Timeout: API javob bermadi")
        return None
    except Exception as e:
        print("Xato:", e)
        return None

def transliterate(arabic_text):
    rules = {"ب": "b", "س": "s", "م": "m", "ا": "a", "ل": "l", "ه": "h", "ر": "r", "ح": "h", "ن": "n", "ي": "y", "ق": "q", "د": "d"}
    return "".join([rules.get(ch, ch) for ch in arabic_text])

@dp.callback_query_handler(lambda c: c.data == "ai_premium_translate")
async def ai_premium_translate(callback: types.CallbackQuery):
    if not check_access(callback.from_user.id):
        await callback.answer("❌ Premium foydalanuvchilar uchun.")
        return
    await callback.message.edit_text("🌍 Premium AI Tarjima rejimi.\n\nMatn yuboring, biz uni kengaytirilgan tarjima qilamiz.")
    await callback.answer()

@dp.message_handler(commands=['addpremium'])
async def add_premium_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("❌ Admin emassiz.")
    try:
        user_id = int(message.get_args())
        update_user(user_id, "is_premium", True)
        await message.answer(f"✅ {user_id} premiumga qo‘shildi.")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

@dp.message_handler(commands=['listpremium'])
async def list_premium_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("❌ Admin emassiz.")
    premium_users = get_premium_users()
    if not premium_users:
        await message.answer("📭 Premium foydalanuvchilar yo‘q.")
    else:
        await message.answer("\n".join([str(u["user_id"]) for u in premium_users]))

async def on_startup(dp):
    global session
    session = aiohttp.ClientSession()
    print("✅ Bot ishga tushdi")

async def on_shutdown(dp):
    await session.close()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
