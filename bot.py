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
from openai import AsyncOpenAI

# ======================
# BOT INIT
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
# ======================
# OPENAI INIT
# ======================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
else:
    ai_client = None

# ===== SURAH CACHE =====
SURAH_CACHE = {}
USER_QORI = {}
USER_QIROAT_MODE = {}

# ======================
# USER MODE MANAGER
# ======================

USER_MODES = {}

def set_user_mode(user_id, mode):
    USER_MODES[user_id] = mode

def get_user_mode(user_id):
    return USER_MODES.get(user_id, "normal")


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
    
def create_card_image(arabic_html, translit, surah_name, ayah):

    width = 900
    height = 700
    side_margin = 100

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    title_font = ImageFont.truetype("DejaVuSans.ttf", 42)

    # ===== TITLE =====
    title = "Qur’oniy oyat"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (bbox[2]-bbox[0]))//2, 40),
              title, fill="#d4af37", font=title_font)

    footer = f"{surah_name} surasi | {ayah}-oyat"
    bbox = draw.textbbox((0, 0), footer, font=title_font)
    draw.text(((width - (bbox[2]-bbox[0]))//2, height-70),
              footer, fill="#d4af37", font=title_font)

    # ===== TAJWID PARSE =====
    segments = parse_tajweed_segments(arabic_html)

    max_width = width - side_margin * 2
    max_height = 320

    arabic_font_size = 95

    # 🔥 AUTO RESIZE LOOP
    while arabic_font_size > 45:

        arabic_font = ImageFont.truetype("Amiri-Regular.ttf", arabic_font_size)

        lines = []
        current_line = []
        line_width = 0

        for rule, segment in segments:

            reshaped = arabic_reshaper.reshape(segment)
            bidi_text = get_display(reshaped)

            bbox = draw.textbbox((0, 0), bidi_text, font=arabic_font)
            seg_width = bbox[2] - bbox[0]

            if line_width + seg_width > max_width:
                lines.append(current_line)
                current_line = []
                line_width = 0

            current_line.append((rule, bidi_text, seg_width))
            line_width += seg_width

        if current_line:
            lines.append(current_line)

        total_height = len(lines) * (arabic_font_size + 25)

        if total_height <= max_height:
            break

        arabic_font_size -= 5

    # ===== DRAW ARABIC =====
    y_text = 140
    line_height = arabic_font_size + 25

    for line in lines:

        total_line_width = sum(seg[2] for seg in line)
        x_cursor = (width + total_line_width) // 2

        for rule, text_part, seg_width in line:

            color = TAJWEED_COLORS.get(rule, "white")

            draw.text(
                (x_cursor - seg_width, y_text),
                text_part,
                font=arabic_font,
                fill=color
            )

            x_cursor -= seg_width

        y_text += line_height

    # ===== TRANSLITERATION AUTO WRAP =====
    translit_font_size = 38
    translit_font = ImageFont.truetype("DejaVuSans.ttf", translit_font_size)

    y_text += 35

    words = translit.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=translit_font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=translit_font)
        draw.text(
            ((width - (bbox[2]-bbox[0]))//2, y_text),
            line,
            fill="#d4af37",
            font=translit_font
        )
        y_text += translit_font_size + 10

    img.save("card.png")
    
# ======================
# SURAH KEYBOARD
# ======================

def surah_keyboard(page=1):
    kb = InlineKeyboardMarkup(row_width=4)

    surahs = get_surahs()
    per_page = 20   # 🔥 20 ta chiqaradi

    total_pages = (len(surahs) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    for surah in surahs[start:end]:
        kb.insert(
            InlineKeyboardButton(
                f"{surah['number']}-sura | {surah['name']}",
                callback_data=f"surah_{surah['number']}"
            )
        )

    nav = []

    if page > 1:
        nav.append(InlineKeyboardButton("⬅", callback_data=f"surahpage_{page-1}"))

    nav.append(InlineKeyboardButton("🏠", callback_data="menu"))

    if page < total_pages:
        nav.append(InlineKeyboardButton("➡", callback_data=f"surahpage_{page+1}"))

    kb.row(*nav)
    return kb

def main_menu():
    kb = InlineKeyboardMarkup(row_width=4)

    kb.row(
        InlineKeyboardButton("📖 Qur'on Tilovati", callback_data="back_to_surah"),
        InlineKeyboardButton("🎧 Professional Qiroat", callback_data="zam_menu")
    )

    kb.row(
        InlineKeyboardButton("🌍 AI Multi-Tarjima", callback_data="ai_translate"),
        InlineKeyboardButton("📜 Fatvo & Hadis AI", callback_data="zikir_ai")
    )

    kb.row(
        InlineKeyboardButton("📚 Tajvidli Mus'haf PDF", callback_data="quron_read")
    )

    return kb



# ======================
# SEND AYAH
# ======================
async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    loading = await message.answer("⏳ Yuklanmoqda...")

    try:
        async with session.get(
            f"https://api.quran.com/api/v4/quran/verses/tajweed?verse_key={surah}:{ayah}"
        ) as resp:
            data = await resp.json()

        if "verses" not in data or not data["verses"]:
            await loading.edit_text("❌ API javob bermadi")
            return

        arabic_html = data["verses"][0].get("text_uthmani_tajweed")

        if not arabic_html:
            arabic_html = data["verses"][0].get("text_uthmani")

        if not arabic_html:
            await loading.edit_text("❌ Oyat topilmadi")
            return

    except Exception as e:
        await loading.edit_text(f"❌ Xatolik: {e}")
        return

    surah_name = f"{surah}-sura"
    translit = ""

    create_card_image(arabic_html, translit, surah_name, ayah)

    await loading.delete()
    await message.answer_photo(InputFile("card.png"))
    total_ayahs = 286  # vaqtincha (navigation ishlashi uchun)

    # ===== AUDIO =====
    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)
    reciter = USER_QORI.get(user_id, "Alafasy_128kbps")
    audio_url = f"https://everyayah.com/data/{reciter}/{sura}{ayah_num}.mp3"

    async with session.get(audio_url) as audio_resp:
        if audio_resp.status == 200:
            import io
            audio_bytes = await audio_resp.read()

            kb_audio = InlineKeyboardMarkup(row_width=3)
            nav_audio = []

            if ayah > 1:
                nav_audio.append(
                    InlineKeyboardButton("⬅ Oldingi", callback_data="prev")
                )

            nav_audio.append(
                InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
            )

            nav_audio.append(
                InlineKeyboardButton("➡ Keyingi", callback_data="next")
            )

            kb_audio.row(*nav_audio)

            await message.answer_audio(
                types.InputFile(
                    io.BytesIO(audio_bytes),
                    filename=f"{sura}{ayah_num}.mp3"
                ),
                reply_markup=kb_audio
            )
# ======================
# HANDLERS
# ======================
# ======================
# ZAM SURALAR
# ======================

QORI_LINKS = {
    "zam_alafasy": "Alafasy_128kbps",
    "zam_badr": "Badr_AlTurki_128kbps",
    "zam_alijon": "Alijon_Qori_128kbps"
}

@dp.callback_query_handler(lambda c: c.data == "zam_menu")
async def zam_menu(callback: types.CallbackQuery):

    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(InlineKeyboardButton("🎙 Badr At-Turkiy", callback_data="qori|Badr_AlTurki_128kbps|1"))
    kb.add(InlineKeyboardButton("🎙 Mishary Alafasy", callback_data="qori|Alafasy_128kbps|1"))
    kb.add(InlineKeyboardButton("🎙 Shayx Alijon", callback_data="qori|Alijon_Qori_128kbps|1"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))

    await callback.message.edit_text(
        "🎧 Professional Qiroat\n\nQorini tanlang:",
        reply_markup=kb
    )

    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("qori|"))
async def qori_page(callback: types.CallbackQuery):

    _, reciter, page = callback.data.split("|")
    page = int(page)

    per_page = 50
    start = (page - 1) * per_page + 1
    end = min(start + per_page - 1, 114)

    kb = InlineKeyboardMarkup(row_width=2)

    # 🔥 Сура номларини API орқали оламиз
    async with session.get("https://api.alquran.cloud/v1/surah") as resp:
        surah_data = await resp.json()

    surahs = surah_data["data"]

    for i in range(start, end + 1):
        surah_name = surahs[i-1]["englishName"]

        kb.insert(
            InlineKeyboardButton(
                f"{i}. {surah_name}",
                callback_data=f"play|{reciter}|{i}"
            )
        )

    nav = []

    # 1️⃣ Orqaga
    if page > 1:
        nav.append(
            InlineKeyboardButton("⬅ Orqaga", callback_data=f"qori|{reciter}|{page-1}")
        )

    # 2️⃣ Qorilar
    nav.append(
        InlineKeyboardButton("🎙 Qorilar", callback_data="zam_menu")
    )

    # 3️⃣ Bosh menyu
    nav.append(
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
    )

    # 4️⃣ Oldinga
    if end < 114:
        nav.append(
            InlineKeyboardButton("➡ Oldinga", callback_data=f"qori|{reciter}|{page+1}")
        )

    kb.row(*nav)
    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=kb
    )

    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("play|"))
async def play_surah(callback: types.CallbackQuery):

    await callback.answer("⏳ Yuklanmoqda...")

    _, reciter, surah_id = callback.data.split("|")
    surah_id = int(surah_id)

    sura = str(surah_id).zfill(3)

    # 🔥 Фақат Mishary ишлайдиган сервер
    @dp.callback_query_handler(lambda c: c.data.startswith("play|"))
    async def play_surah(callback: types.CallbackQuery):

        await callback.answer("⏳ Yuklanmoqda...")

        _, reciter, surah_id = callback.data.split("|")
        surah_id = int(surah_id)

        sura = str(surah_id).zfill(3)

        FOLDERS = {
            "Alafasy_128kbps": "Alafasy_128kbps",
            "Badr_AlTurki_128kbps": "Badr_AlTurki_128kbps",
            "Alijon_Qori_128kbps": "Alijon_Qori_128kbps"
        }

        folder = FOLDERS.get(reciter)

        if not folder:
            await callback.message.answer("Qori topilmadi ❌")
            return

        audio_url = f"https://everyayah.com/data/{folder}/{sura}001.mp3"

        await callback.message.answer_audio(audio=audio_url)

        await callback.message.answer_audio(audio=audio_url)
    
@dp.callback_query_handler(lambda c: c.data.startswith("qori_"))
async def select_qori(callback: types.CallbackQuery):

    qori_map = {
        "qori_badr": "Badr_AlTurki_128kbps",
        "qori_alafasy": "Alafasy_128kbps",
        "qori_alijon": "Alijon_Qori_128kbps"
    }

    USER_QORI[callback.from_user.id] = qori_map[callback.data]
    USER_QIROAT_MODE[callback.from_user.id] = True

    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=surah_keyboard()
    )

    await callback.answer()



@dp.callback_query_handler(lambda c: c.data.startswith("zam_"))
async def zam_play(callback: types.CallbackQuery):

    user = get_user(callback.from_user.id)

    surah = user.get("current_surah", 1)
    ayah = 1   # 🔥 HAR DOIM BOSHDAN

    reciter = QORI_LINKS.get(callback.data)

    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)

    audio_url = f"https://everyayah.com/data/{reciter}/{sura}{ayah_num}.mp3"

    async with session.get(audio_url) as audio_resp:
        if audio_resp.status == 200:
            import io
            audio_bytes = await audio_resp.read()

            await callback.message.answer_audio(
                types.InputFile(
                    io.BytesIO(audio_bytes),
                    filename=f"{sura}{ayah_num}.mp3"
                )
            )
        else:
            await callback.message.answer("Audio topilmadi ❌")

    await callback.answer()
@dp.callback_query_handler(lambda c: c.data == "quron_read")
async def quron_read(callback: types.CallbackQuery):
    await callback.message.answer_document(
        InputFile("tajwid_mushaf.pdf"),
        caption="📖 Tajvidli Qur’on kitobi"
    )
    await callback.answer()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):

    get_user(message.from_user.id)

    text = (
        "🕌 *QUR’ON INTELLECT PLATFORM*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 Tilovat & Tafakkur\n"
        "🎧 Qiroat & Audio\n"
        "🌍 AI Tarjima Markazi\n"
        "📜 Fatvo va Dalil AI\n"
        "📚 Tajvidli Mus'haf\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "_Ilm • Tafakkur • Amal_"
    )

    await message.answer(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

   

async def show_ayah_page(callback, surah_number, page, total_ayahs):

    per_page = 20   # 🔥 20 ta

    start = (page - 1) * per_page + 1
    end = min(start + per_page - 1, total_ayahs)

    kb = InlineKeyboardMarkup(row_width=4)

    title = f"📖 {surah_number}-sura | {start}-{end}-oyatlar"

    for i in range(start, end + 1):
        kb.insert(
            InlineKeyboardButton(
                f"{i}-oyat",
                callback_data=f"ayah_{i}"
            )
        )

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅", callback_data=f"ayahpage_{page-1}")
        )

    nav_buttons.append(
        InlineKeyboardButton("🏠", callback_data="menu")
    )

    if end < total_ayahs:
        nav_buttons.append(
            InlineKeyboardButton("➡", callback_data=f"ayahpage_{page+1}")
        )

    kb.row(*nav_buttons)

    await callback.message.edit_text(
        title,
        reply_markup=kb
    )

    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("surahpage_"))
async def surah_page(callback: types.CallbackQuery):

    page = int(callback.data.split("_")[1])

    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=surah_keyboard(page)
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if USER_QIROAT_MODE.get(user_id):

        surah_id = int(callback.data.split("_")[1])
        USER_QIROAT_MODE[user_id] = False

        reciter = USER_QORI.get(user_id, "Alafasy_128kbps")

        sura = str(surah_id).zfill(3)
        audio_url = f"https://everyayah.com/data/{reciter}/{sura}001.mp3"

        async with session.get(audio_url) as audio_resp:
            if audio_resp.status == 200:
                import io
                audio_bytes = await audio_resp.read()

                await callback.message.answer_audio(
                    types.InputFile(
                        io.BytesIO(audio_bytes),
                        filename=f"{sura}001.mp3"
                    )
                )

        await callback.answer()
        

    user_id = callback.from_user.id
    surah_id = int(callback.data.split("_")[1])
    print("SURAH BOSILDI")

    update_user(callback.from_user.id, "current_surah", surah_id)
    update_user(callback.from_user.id, "current_ayah", 1)
    if surah_id not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_id}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah_id] = r['data']['numberOfAyahs']
            surah_info = r['data']
    else:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_id}") as resp:
            r = await resp.json()
            surah_info = r['data']

    total_ayahs = SURAH_CACHE[surah_id]

    info_text = (
        f"📖 *{surah_info['englishName']} surasi*\n\n"
        f"• Oyatlar soni: {surah_info['numberOfAyahs']}\n"
        f"• Nozil bo‘lgan joyi: {surah_info['revelationType']}\n\n"
        f"Oyatni tanlang:"
    )

    await callback.message.edit_text(
        info_text,
        parse_mode="Markdown"
    )

    await show_ayah_page(callback, surah_id, 1, total_ayahs)

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("ayahpage_"))
async def ayah_page_handler(callback: types.CallbackQuery):

    page = int(callback.data.split("_")[1])

    user = get_user(callback.from_user.id)
    surah_number = user["current_surah"]

    if surah_number not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_number}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah_number] = r['data']['numberOfAyahs']

    total_ayahs = SURAH_CACHE[surah_number]

    await show_ayah_page(callback, surah_number, page, total_ayahs)


@dp.callback_query_handler(lambda c: c.data.startswith("ayah_"))
async def select_ayah(callback: types.CallbackQuery):

    await callback.answer()

    ayah = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_ayah", ayah)

    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()



@dp.callback_query_handler(lambda c: c.data == "ai_translate")
async def enable_translate(callback: types.CallbackQuery):

    set_user_mode(callback.from_user.id, "translate")

    text = (
        "🌍 *AI Tarjima rejimi*\n\n"
        "Istalgan matnni yuboring.\n"
        "Men uni professional tarzda tarjima qilaman."
    )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()



@dp.callback_query_handler(lambda c: c.data == "zikir_ai")
async def enable_zikir(callback: types.CallbackQuery):

    set_user_mode(callback.from_user.id, "zikir")

    text = (
        "🕌 *Fatvo AI rejimi*\n\n"
        "Savolingizni yozing.\n"
        "Javob dalillar bilan beriladi."
    )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()



@dp.callback_query_handler(lambda c: c.data == "back_to_surah")
async def back_to_surah(callback: types.CallbackQuery):

    set_user_mode(callback.from_user.id, "normal")

    text = (
        "📖 *Qur’on o‘qish rejimi*\n\n"
        "Sura tanlang va oyatlarni professional formatda o‘qing."
    )

    await callback.message.edit_text(
        text,
        reply_markup=surah_keyboard(),
        parse_mode="Markdown"
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data in ["next", "prev", "menu"])
async def navigation(callback: types.CallbackQuery):

    user_id = callback.from_user.id
    user = get_user(user_id)

    surah = user["current_surah"]
    ayah = user["current_ayah"]

    if callback.data == "menu":
        set_user_mode(user_id, "normal")
        await callback.message.answer(
            "🕌 *QUR’ON INTELLECT PLATFORM*",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    if surah not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah] = r['data']['numberOfAyahs']

    total_ayahs = SURAH_CACHE[surah]

    if callback.data == "next" and ayah < total_ayahs:
        update_user(user_id, "current_ayah", ayah + 1)

    elif callback.data == "prev" and ayah > 1:
        update_user(user_id, "current_ayah", ayah - 1)

    await callback.answer()
    await send_ayah(user_id, callback.message)


@dp.message_handler()
async def universal_handler(message: types.Message):

    mode = get_user_mode(message.from_user.id)

    if not ai_client:
        return

    if mode == "translate":

        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a real-time translator."},
                {"role": "user", "content": message.text}
            ]
        )

        await message.answer(response.choices[0].message.content)

    elif mode == "zikir":

        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Islamic scholar. Answer with hadith evidence and Uzbekistan Fatwa references."
                },
                {"role": "user", "content": message.text}
            ]
        )

        await message.answer(response.choices[0].message.content)




# ======================
# STARTUP / SHUTDOWN
# ======================

async def on_startup(dp):
    global session
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
    print("✅ Session started")


async def on_shutdown(dp):
    await session.close()
    print("❌ Session closed")


# ======================
# RUN
# ======================

# ======================
# WEBHOOK MODE (RENDER)
# ======================

from aiogram.utils.executor import start_webhook

WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def on_startup_webhook(dp):
    await on_startup(dp)
    await bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set:", WEBHOOK_URL)

async def on_shutdown_webhook(dp):
    await bot.delete_webhook()
    await on_shutdown(dp)
    print("❌ Webhook deleted")

if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )

