import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_surahs, get_user, update_user, get_ayah

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def remove_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

asyncio.get_event_loop().run_until_complete(remove_webhook())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# SURAH LIST
# ======================

surahs = get_surahs()

def surah_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)

    for surah in surahs:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}",
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

    await send_ayah(callback.from_user.id, callback.message)

# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user[1]
    ayah = user[2]

    data = get_ayah(surah, ayah)

    text = f"""
📖 {data['surah_name']} сураси
Оят: {ayah}

{data['arabic']}

{data['uzbek']}
"""

    kb = InlineKeyboardMarkup()

    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Олдинги", callback_data="prev"))

    if ayah < data['total_ayahs']:
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

    surah = user[1]
    ayah = user[2]

    if callback.data == "next":
        update_user(user_id, "current_ayah", ayah + 1)

    elif callback.data == "prev":
        update_user(user_id, "current_ayah", ayah - 1)

    elif callback.data == "menu":
        await callback.message.answer(
            "📖 Сурани танланг:",
            reply_markup=surah_keyboard()
        )
        return

    await send_ayah(user_id, callback.message)

# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
