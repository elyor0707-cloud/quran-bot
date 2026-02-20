import os
import aiohttp
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from database import get_surahs, get_user, update_user
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from openai import AsyncOpenAI

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

session = None
SURAH_CACHE = {}
USER_MODES = {}

# ======================
# TAJWEED COLORS
# ======================

TAJWEED_COLORS = {
    "ghunnah": "#2ecc71",
    "idgham": "#3498db",
    "ikhfa": "#9b59b6",
    "qalqalah": "#e74c3c",
    "iqlab": "#f39c12",
}

def clean_tajweed_text(text):
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
        segments.append((match.group(1), match.group(2)))
        pos = end

    if pos < len(text):
        segments.append(("normal", text[pos:]))

    return segments

# ======================
# IMAGE GENERATOR
# ======================

def create_card_image(arabic_html, uzbek, surah_name, ayah):

    width = 900
    height = 650
    side_margin = 110

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("ScheherazadeNew-Regular.ttf", 72)
    uzbek_font = ImageFont.truetype("DejaVuSans.ttf", 34)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 45)

    # TITLE
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (bbox[2]-bbox[0]))//2, 40),
              title, fill="#d4af37", font=title_font)

    # FOOTER
    footer = f"{surah_name} surasi, {ayah}-oyat"
    bbox = draw.textbbox((0, 0), footer, font=title_font)
    footer_y = height - (bbox[3]-bbox[1]) - 40
    draw.text(((width - (bbox[2]-bbox[0]))//2, footer_y),
              footer, fill="#d4af37", font=title_font)

    # ARABIC
    segments = parse_tajweed_segments(arabic_html)
    max_width = width - side_margin * 2
    y_text = 120
    lines = []
    current_line = []
    current_width = 0

    for rule, part in segments:
        reshaped = arabic_reshaper.reshape(part)
        bidi_text = get_display(reshaped)
        bbox = draw.textbbox((0, 0), bidi_text, font=arabic_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if current_width + w > max_width:
            lines.append(current_line)
            current_line = []
            current_width = 0

        current_line.append((rule, bidi_text, w, h))
        current_width += w

    if current_line:
        lines.append(current_line)

    for line in lines:
        total_width = sum(part[2] for part in line)
        x_cursor = (width + total_width) // 2
        max_h = 0

        for rule, text_part, w, h in line:
            color = TAJWEED_COLORS.get(rule, "white")
            draw.text((x_cursor - w, y_text),
                      text_part, fill=color, font=arabic_font)
            x_cursor -= w
            max_h = max(max_h, h)

        y_text += max_h + 20

    # TRANSLATION
    y_text += 20
    words = uzbek.split()
    line = ""

    for word in words:
        test_line = line + " " + word if line else word
        bbox = draw.textbbox((0, 0), test_line, font=uzbek_font)
        if bbox[2]-bbox[0] <= max_width:
            line = test_line
        else:
            draw.text(((width - (bbox[2]-bbox[0]))//2, y_text),
                      line, fill="white", font=uzbek_font)
            y_text += 40
            line = word

    if line:
        draw.text(((width - (bbox[2]-bbox[0]))//2, y_text),
                  line, fill="white", font=uzbek_font)

    img.save("card.png")

# ======================
# KEYBOARDS
# ======================

def surah_keyboard(page=1):
    kb = InlineKeyboardMarkup(row_width=4)
    surahs = get_surahs()
    per_page = 20

    total_pages = (len(surahs) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    for surah in surahs[start:end]:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}. {surah['name']}",
                callback_data=f"surah_{surah['number']}"
            )
        )

    if page > 1:
        kb.insert(InlineKeyboardButton("⬅", callback_data=f"surahpage_{page-1}"))
    if page < total_pages:
        kb.insert(InlineKeyboardButton("➡", callback_data=f"surahpage_{page+1}"))

    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    return kb

# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):
    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    async with session.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-tajweed,uz.sodik"
    ) as resp:
        r = await resp.json()

    arabic_html = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']
    total_ayahs = r['data'][0]['surah']['numberOfAyahs']

    create_card_image(arabic_html, uzbek, surah_name, ayah)
    await message.answer_photo(InputFile("card.png"))

    # AUDIO
    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)
    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

    async with session.get(audio_url) as audio_resp:
        if audio_resp.status == 200:
            import io
            audio_bytes = await audio_resp.read()
            await message.answer_audio(
                types.InputFile(io.BytesIO(audio_bytes),
                                filename=f"{sura}{ayah_num}.mp3")
            )

    # NAV
    kb = InlineKeyboardMarkup(row_width=3)
    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Oldingi", callback_data="prev"))
    if ayah < total_ayahs:
        kb.insert(InlineKeyboardButton("➡ Keyingi", callback_data="next"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))

    await message.answer("👇", reply_markup=kb)

# ======================
# HANDLERS
# ======================
# ======================
# SURAH TANLASH
# ======================

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):

    surah_number = int(callback.data.split("_")[1])

    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)

    if surah_number not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_number}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah_number] = r['data']['numberOfAyahs']

    total_ayahs = SURAH_CACHE[surah_number]

    await show_ayah_page(callback, surah_number, 1, total_ayahs)
    await callback.answer()


# ======================
# OYAT PAGE
# ======================

async def show_ayah_page(callback, surah_number, page, total_ayahs):

    per_page = 10
    start = (page - 1) * per_page + 1
    end = min(start + per_page - 1, total_ayahs)

    kb = InlineKeyboardMarkup(row_width=5)

    for i in range(start, end + 1):
        kb.insert(
            InlineKeyboardButton(
                f"{i}",
                callback_data=f"ayah_{i}"
            )
        )

    nav = []

    if page > 1:
        nav.append(
            InlineKeyboardButton("⬅", callback_data=f"ayahpage_{page-1}")
        )

    nav.append(
        InlineKeyboardButton("🏠", callback_data="menu")
    )

    if end < total_ayahs:
        nav.append(
            InlineKeyboardButton("➡", callback_data=f"ayahpage_{page+1}")
        )

    kb.row(*nav)

    await callback.message.edit_text(
        f"📖 {surah_number}-sura | {start}-{end} oyatlar",
        reply_markup=kb
    )


@dp.callback_query_handler(lambda c: c.data.startswith("ayahpage_"))
async def ayah_page_handler(callback: types.CallbackQuery):

    page = int(callback.data.split("_")[1])
    user = get_user(callback.from_user.id)
    surah = user["current_surah"]

    total_ayahs = SURAH_CACHE.get(surah)

    if not total_ayahs:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah}") as resp:
            r = await resp.json()
            total_ayahs = r['data']['numberOfAyahs']
            SURAH_CACHE[surah] = total_ayahs

    await show_ayah_page(callback, surah, page, total_ayahs)
    await callback.answer()


# ======================
# OYAT TANLASH
# ======================

@dp.callback_query_handler(lambda c: c.data.startswith("ayah_"))
async def select_ayah(callback: types.CallbackQuery):

    ayah = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_ayah", ayah)

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

    if callback.data == "menu":
        await callback.message.edit_text(
            "📖 Surani tanlang:",
            reply_markup=surah_keyboard()
        )
        await callback.answer()
        return

    total_ayahs = SURAH_CACHE.get(surah)

    if not total_ayahs:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah}") as resp:
            r = await resp.json()
            total_ayahs = r['data']['numberOfAyahs']
            SURAH_CACHE[surah] = total_ayahs

    if callback.data == "next" and ayah < total_ayahs:
        update_user(user_id, "current_ayah", ayah + 1)

    elif callback.data == "prev" and ayah > 1:
        update_user(user_id, "current_ayah", ayah - 1)

    await send_ayah(user_id, callback.message)
    await callback.answer()
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("📖 Surani tanlang:",
                         reply_markup=surah_keyboard())

# ======================
# STARTUP / SHUTDOWN
# ======================

async def on_startup(dp):
    global session
    session = aiohttp.ClientSession()
    print("✅ Session started")

async def on_shutdown(dp):
    await session.close()
    print("❌ Session closed")

if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
