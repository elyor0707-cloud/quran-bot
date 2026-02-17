from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import requests
from database import get_surahs, get_user, update_user
from aiogram.types import InputFile
from PIL import Image, ImageDraw, ImageFont

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
# SEND AYAH (AUDIO WITH REAL API)
# ======================

import os

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_ayah_image(arabic_text, filename="ayah.png"):
    width = 1600
    height = 1000
    margin = 150
    line_spacing = 60   # 🔥 qator oralig‘i oshdi

    # 🔹 Yumshoq fon
    img = Image.new("RGB", (width, height), "#f5f1e6")
    draw = ImageDraw.Draw(img)

    font_path = os.path.join(os.getcwd(), "Amiri-Regular.ttf")
    font = ImageFont.truetype(font_path, 170)

    # 🔹 Qatorlarga bo‘lish
    wrapped_text = textwrap.fill(arabic_text, width=22)
    lines = wrapped_text.split("\n")

    # 🔹 Umumiy balandlikni hisoblash
    total_height = 0
    line_sizes = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        total_height += h + line_spacing
        line_sizes.append((w, h))

    total_height -= line_spacing

    y = (height - total_height) / 2

    for i, line in enumerate(lines):
        w, h = line_sizes[i]

        # 🔥 HAQIQIY markazlashtirish
        x = (width - w) / 2

        draw.text((x, y), line, fill="#222222", font=font)
        y += h + line_spacing

    img.save(filename)

async def send_ayah(user_id, message):

    user = get_user(user_id)

    surah = user["current_surah"]
    ayah = user["current_ayah"]

    r = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,uz.sodik"
    ).json()

    arabic = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']
    total_ayahs = r['data'][0]['surah']['numberOfAyahs']

    # 🖼 PNG яратиш
    create_ayah_image(arabic)
    await message.answer_photo(InputFile("ayah.png"))

    text = f"""
📖 {surah_name} сураси
Оят: {ayah}

{uzbek}
"""

    kb = InlineKeyboardMarkup()

    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Олдинги", callback_data="prev"))

    if ayah < total_ayahs:
        kb.insert(InlineKeyboardButton("➡ Кейинги", callback_data="next"))

    kb.add(InlineKeyboardButton("🏠 Бош меню", callback_data="menu"))

    await message.answer(text, reply_markup=kb)

    # 🔊 AUDIO
    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)
    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

    try:
        audio_file = requests.get(audio_url, timeout=10)
        if audio_file.status_code == 200:
            filename = f"{sura}{ayah_num}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_file.content)

            await message.answer_audio(InputFile(filename))
        else:
            await message.answer("🔊 Аудио топилмади.")
    except:
        await message.answer("🔊 Аудио юклашда хато.")


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
