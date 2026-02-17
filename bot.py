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
# IMAGE CARD (2-KO'RINISH)
# =========================

def create_card(arabic, uzbek, surah_name, ayah):

    width = 1200
    height = 900
    margin = 120

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("Amiri-Regular.ttf", 72)
    uzbek_font = ImageFont.truetype("DejaVuSans.ttf", 34)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 45)

    # TITLE
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0,0), title, font=title_font)
    draw.text(((width - (bbox[2]-bbox[0]))//2, 40),
              title, fill="#d4af37", font=title_font)

    # FOOTER
    footer = f"{surah_name} surasi, {ayah}-oyat"
    bbox = draw.textbbox((0,0), footer, font=title_font)
    footer_y = height - (bbox[3]-bbox[1]) - 40
    draw.text(((width - (bbox[2]-bbox[0]))//2, footer_y),
              footer, fill="#d4af37", font=title_font)

    # ================= ARABIC =================

    reshaped = arabic_reshaper.reshape(arabic)
    bidi_text = get_display(reshaped)

    max_width = width - margin*2
    y = 140

    words = bidi_text.split(" ")
    line = ""

    for word in words:
        test_line = line + " " + word if line else word
        bbox = draw.textbbox((0,0), test_line, font=arabic_font)
        w = bbox[2] - bbox[0]

        if w <= max_width:
            line = test_line
        else:
            bbox = draw.textbbox((0,0), line, font=arabic_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width-lw)//2, y), line,
                      fill="white", font=arabic_font)
            y += 80
            line = word

    if line:
        bbox = draw.textbbox((0,0), line, font=arabic_font)
        lw = bbox[2] - bbox[0]
        draw.text(((width-lw)//2, y), line,
                  fill="white", font=arabic_font)
        y += 80

    # SARIQ CHIZIQ
    draw.line((margin, y, width-margin, y),
              fill="#d4af37", width=3)

    # ================= TARJIMA =================

    y += 30
    limit = footer_y - 20
    line = ""

    words = uzbek.split()

    for word in words:
        test_line = line + " " + word if line else word
        bbox = draw.textbbox((0,0), test_line, font=uzbek_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_width:
            line = test_line
        else:
            if y + h > limit:
                break

            bbox = draw.textbbox((0,0), line, font=uzbek_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width-lw)//2, y), line,
                      fill="white", font=uzbek_font)
            y += h + 8
            line = word

    if line:
        bbox = draw.textbbox((0,0), line, font=uzbek_font)
        lw = bbox[2] - bbox[0]
        draw.text(((width-lw)//2, y), line,
                  fill="white", font=uzbek_font)

    img.save("card.png")

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

    create_card(arabic, uzbek, surah_name, ayah)
await message.answer_photo(InputFile("card.png"))

# AUDIO
sura = str(surah).zfill(3)
ayah_num = str(ayah).zfill(3)
audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

await message.answer_audio(audio_url)


# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
