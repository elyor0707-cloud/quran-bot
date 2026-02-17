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
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =======================
# TAJWEED CLEAN
# =======================

def clean_tajweed_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text

# =======================
# IMAGE GENERATOR
# =======================

def create_card_image(arabic_html, uzbek, surah_name, ayah):

    width = 1200
    height = 900
    margin = 110

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("Amiri-Regular.ttf", 70)
    uzbek_font = ImageFont.truetype("DejaVuSans.ttf", 34)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 45)

    # TITLE
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw)//2, 40), title, fill="#d4af37", font=title_font)

    # FOOTER
    footer = f"{surah_name} surasi, {ayah}-oyat"
    bbox = draw.textbbox((0, 0), footer, font=title_font)
    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]
    footer_y = height - fh - 40
    draw.text(((width - fw)//2, footer_y), footer, fill="#d4af37", font=title_font)

    # ================= ARABIC =================

    arabic_text = clean_tajweed_text(arabic_html)
    reshaped = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped)

    max_width = width - margin*2
    words = bidi_text.split(" ")

    lines = []
    line = ""
    for word in words:
        test = line + " " + word if line else word
        bbox = draw.textbbox((0,0), test, font=arabic_font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    y = 130
    for ln in lines:
        bbox = draw.textbbox((0,0), ln, font=arabic_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w)//2, y), ln, fill="white", font=arabic_font)
        y += h + 20

    # SEPARATOR
    line_y = y + 10
    draw.line((margin, line_y, width - margin, line_y), fill="#d4af37", width=3)

    # ================= TRANSLATION =================

    y = line_y + 30
    limit_bottom = footer_y - 20
    max_width = width - margin*2

    words = uzbek.split()
    line = ""

    for word in words:
        test = line + " " + word if line else word
        bbox = draw.textbbox((0,0), test, font=uzbek_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_width:
            line = test
        else:
            if y + h > limit_bottom:
                break
            bbox = draw.textbbox((0,0), line, font=uzbek_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw)//2, y), line, fill="white", font=uzbek_font)
            y += h + 8
            line = word

    if line:
        bbox = draw.textbbox((0,0), line, font=uzbek_font)
        lw = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if y + h <= limit_bottom:
            draw.text(((width - lw)//2, y), line, fill="white", font=uzbek_font)

    img.save("card.png")

# =======================
# KEYBOARD
# =======================

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📖 Surani tanlang", callback_data="surah_menu"))
    kb.add(InlineKeyboardButton("📊 Statistika", callback_data="stat"))
    return kb

def surah_keyboard():
    kb = InlineKeyboardMarkup(row_width=4)
    surahs = get_surahs()
    for s in surahs:
        kb.insert(InlineKeyboardButton(
            f"{s['number']}. {s['name']}",
            callback_data=f"surah_{s['number']}"
        ))
    return kb

# =======================
# SEND AYAH
# =======================

async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,uz.sodik"
        ) as resp:
            r = await resp.json()

    arabic_html = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']

    update_user(user_id, "last_surah", surah)
    update_user(user_id, "last_ayah", ayah)

    create_card_image(arabic_html, uzbek, surah_name, ayah)
    await message.answer_photo(InputFile("card.png"))

# =======================
# HANDLERS
# =======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("Асосий меню:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == "surah_menu")
async def open_surah_menu(callback: types.CallbackQuery):
    await callback.message.answer("Сурани танланг:", reply_markup=surah_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):
    surah_number = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)
    await send_ayah(callback.from_user.id, callback.message)

@dp.callback_query_handler(lambda c: c.data == "stat")
async def show_stat(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user.get("last_surah"):
        await callback.message.answer(
            f"Oxirgi o‘qilgan:\nSura: {user['last_surah']}\nOyat: {user['last_ayah']}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("▶ Davom etish", callback_data="continue")
            )
        )
    else:
        await callback.message.answer("Hali o‘qilmagan.")

@dp.callback_query_handler(lambda c: c.data == "continue")
async def continue_read(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    update_user(callback.from_user.id, "current_surah", user["last_surah"])
    update_user(callback.from_user.id, "current_ayah", user["last_ayah"])
    await send_ayah(callback.from_user.id, callback.message)

# =======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
