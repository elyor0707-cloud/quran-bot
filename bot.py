from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

from database import get_surahs, get_user, update_user, get_ayah

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# SURAH LIST
# ======================

def surah_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    surahs = get_surahs()

    row = []
    for surah in surahs:
        button = InlineKeyboardButton(
            f"{surah['number']}. Сура {surah['number']}",
            callback_data=f"surah_{surah['number']}"
        )
        row.append(button)

        if len(row) == 3:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

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
