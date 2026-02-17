import os
import aiohttp
import asyncio
import textwrap
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from database import get_surahs, get_user, update_user
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import re

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

TAJWEED_COLORS = {
    "ghunnah": "#2ecc71",
    "idgham": "#3498db",
    "ikhfa": "#9b59b6",
    "qalqalah": "#e74c3c",
    "iqlab": "#f39c12",
}

def clean_tajweed_text(text):
    # Remove internal markers like [h:1], [n], etc.
    text = re.sub(r'\[.*?\]', '', text)
    return text


def parse_tajweed_segments(text):
    text = clean_tajweed_text(text)

    segments = []
    pattern = r'<tajweed class="(.*?)">(.*?)</tajweed>'

    pos = 0
    for match in re.finditer(pattern, text):
        start, end = match.span()

        if start > pos:
            segments.append(("normal", text[pos:start]))

        rule = match.group(1)
        content = match.group(2)
        segments.append((rule, content))

        pos = end

    if pos < len(text):
        segments.append(("normal", text[pos:]))

    return segments

# ======================
# IMAGE CARD GENERATOR
# ======================

def draw_multiline_text(draw, text, font, max_width, start_y, width, line_spacing=10):

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(((width - w)/2, y), line, fill="white", font=font)
        y += h + line_spacing

    return y
    
def create_card_image(arabic_html, uzbek, surah_name, ayah):

    width = 1200
    height = 900

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("Amiri-Regular.ttf", 75)
    uzbek_font = ImageFont.truetype("DejaVuSans.ttf", 32)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 45)

    # ================= TITLE =================
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw)/2, 40), title, fill="#d4af37", font=title_font)

    # ================= ARABIC =================
    segments = parse_tajweed_segments(arabic_html)

    y_text = 120   # <<< ARABIC YUQORIROQ
    x_cursor = width - 150
    max_left = 150
    max_line_height = 0

    for rule, part in segments:

        reshaped = arabic_reshaper.reshape(part)
        bidi_part = get_display(reshaped)

        color = TAJWEED_COLORS.get(rule, "white")

        bbox = draw.textbbox((0, 0), bidi_part, font=arabic_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if x_cursor - w < max_left:
            y_text += max_line_height + 20
            x_cursor = width - 150
            max_line_height = 0

        draw.text((x_cursor - w, y_text), bidi_part, fill=color, font=arabic_font)

        x_cursor -= w
        max_line_height = max(max_line_height, h)

    arabic_bottom = y_text + max_line_height

    # ================= LINE =================
    line_y = arabic_bottom + 20
    draw.line((200, line_y, width-200, line_y), fill="#d4af37", width=3)

    # ================= UZBEK =================
    translation_y = line_y + 40   # <<< TARJIMA PASTROQ

    translation_bottom = draw_multiline_text(
        draw,
        uzbek,
        uzbek_font,
        width - 300,
        translation_y,
        width,
        line_spacing=8
    )

    # ================= FOOTER =================
    footer = f"{surah_name} surasi, {ayah}-oyat"
    bbox = draw.textbbox((0, 0), footer, font=title_font)
    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]

    footer_y = translation_bottom + 30

    # Agar juda pastga tushsa, balandlikni cheklaymiz
    if footer_y + fh > height - 40:
        footer_y = height - fh - 40

    draw.text(((width - fw)/2, footer_y), footer, fill="#d4af37", font=title_font)

    img.save("card.png")



# ======================
# SURAH KEYBOARD
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
# SEND AYAH
# ======================

async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    async with aiohttp.ClientSession() as session:

        async with session.get(
            f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-tajweed,uz.sodik"
        ) as resp:
            r = await resp.json()

        arabic_html = r['data'][0]['text']
        uzbek = r['data'][1]['text']
        surah_name = r['data'][0]['surah']['englishName']
        total_ayahs = r['data'][0]['surah']['numberOfAyahs']
        import re

        
        # IMAGE
        create_card_image(arabic_html, uzbek, surah_name, ayah)
        await message.answer_photo(InputFile("card.png"))

        # AUDIO
        sura = str(surah).zfill(3)
        ayah_num = str(ayah).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        async with session.get(audio_url) as audio_resp:
            if audio_resp.status == 200:
                filename = f"{sura}{ayah_num}.mp3"
                with open(filename, "wb") as f:
                    f.write(await audio_resp.read())

                await message.answer_audio(InputFile(filename))
                os.remove(filename)
            else:
                await message.answer("🔊 Audio topilmadi.")

    # NAVIGATION
    kb = InlineKeyboardMarkup()

    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Oldingi", callback_data="prev"))

    if ayah < total_ayahs:
        kb.insert(InlineKeyboardButton("➡ Keyingi", callback_data="next"))

    kb.add(InlineKeyboardButton("🏠 Bosh menu", callback_data="menu"))

    await message.answer("👇 Navigatsiya:", reply_markup=kb)


# ======================
# HANDLERS
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("📖 Surani tanlang:", reply_markup=surah_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):

    surah_number = int(callback.data.split("_")[1])

    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)

    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()


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
        await callback.message.answer("📖 Surani tanlang:", reply_markup=surah_keyboard())
        await callback.answer()
        return

    await send_ayah(user_id, callback.message)
    await callback.answer()


# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
