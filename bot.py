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
    side_margin = 110

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("Amiri-Regular.ttf", 72)
    uzbek_font = ImageFont.truetype("DejaVuSans.ttf", 34)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 45)

    # ================= TITLE =================
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw)//2, 40), title, fill="#d4af37", font=title_font)

    # ================= FOOTER =================
    footer = f"{surah_name} surasi, {ayah}-oyat"
    bbox = draw.textbbox((0, 0), footer, font=title_font)
    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]
    footer_y = height - fh - 40
    draw.text(((width - fw)//2, footer_y), footer, fill="#d4af37", font=title_font)

    
        # ================= ARABIC AUTO FIT =================
    
       # ================= ARABIC MULTI-LINE RTL =================
    segments = parse_tajweed_segments(arabic_html)

    max_width = width - side_margin * 2
    y_text = 120

    lines = []
    current_line = []
    current_width = 0

    # --- SATRGA AJRATISH ---
    for rule, part in segments:

        reshaped = arabic_reshaper.reshape(part)
        bidi_text = get_display(reshaped)

        bbox = draw.textbbox((0, 0), bidi_text, font=arabic_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # Агар ҳозирги сатрга сиғмаса → янги сатр
        if current_width + w > max_width:
            lines.append(current_line)
            current_line = []
            current_width = 0

        current_line.append((rule, bidi_text, w, h))
        current_width += w

    if current_line:
        lines.append(current_line)

    # --- CHIZISH (RTL) ---
    for line in lines:

        total_line_width = sum(part[2] for part in line)
        x_cursor = (width + total_line_width) // 2  # марказлашган RTL
        max_h = 0

        for rule, text_part, w, h in line:
            color = TAJWEED_COLORS.get(rule, "white")
            draw.text((x_cursor - w, y_text), text_part, fill=color, font=arabic_font)
            x_cursor -= w
            max_h = max(max_h, h)

        y_text += max_h + 20


    # ================= SEPARATOR =================
    line_y = y_text + 10
    draw.line((side_margin, line_y, width - side_margin, line_y), fill="#d4af37", width=3)

    # ================= TRANSLATION =================
    y_text = line_y + 30
    max_text_width = width - side_margin * 2
    limit_bottom = footer_y - 20

    words = uzbek.split()
    line = ""

    for word in words:
        test_line = line + " " + word if line else word
        bbox = draw.textbbox((0, 0), test_line, font=uzbek_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_text_width:
            line = test_line
        else:
            if y_text + h > limit_bottom:
                break

            bbox = draw.textbbox((0, 0), line, font=uzbek_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw)//2, y_text), line, fill="white", font=uzbek_font)

            y_text += h + 8
            line = word

    if line:
        bbox = draw.textbbox((0, 0), line, font=uzbek_font)
        lw = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if y_text + h <= limit_bottom:
            draw.text(((width - lw)//2, y_text), line, fill="white", font=uzbek_font)

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

@dp.callback_query_handler(lambda c: c.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        "📖 Surani tanlang:",
        reply_markup=surah_keyboard()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):

    parts = callback.data.split("_")
    surah_number = int(parts[1])

    # pagination offset
    if len(parts) == 3:
        offset = int(parts[2])
    else:
        offset = 0

    update_user(callback.from_user.id, "current_surah", surah_number)
@dp.callback_query_handler(lambda c: c.data.startswith("ayah_"))
async def select_ayah(callback: types.CallbackQuery):

    ayah = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_ayah", ayah)

    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()

    # Оятлар сонини оламиз
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}"
        ) as resp:
            r = await resp.json()

    total_ayahs = r['data']['numberOfAyahs']

    start = offset + 1
    end = min(offset + 50, total_ayahs)

    kb = InlineKeyboardMarkup(row_width=6)

    # ===== OYATLAR =====
    for i in range(start, end + 1):
        kb.insert(
            InlineKeyboardButton(
                str(i),
                callback_data=f"ayah_{i}"
            )
        )

    # ===== PAGINATION =====
    nav_buttons = []

    if offset > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅ Oldingi 50",
                callback_data=f"surah_{surah_number}_{max(0, offset-50)}"
            )
        )

    if end < total_ayahs:
        nav_buttons.append(
            InlineKeyboardButton(
                "➡ Keyingi 50",
                callback_data=f"surah_{surah_number}_{offset+50}"
            )
        )

    if nav_buttons:
        kb.row(*nav_buttons)

    kb.add(
        InlineKeyboardButton("🏠 Bosh menu", callback_data="menu")
    )

    await callback.message.answer(
        f"{surah_number}-sura | {start}-{end} оятлар",
        reply_markup=kb
    )

    await callback.answer()


# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
