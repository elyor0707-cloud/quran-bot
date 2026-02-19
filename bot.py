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
    
def create_card_image(arabic_html, uzbek, surah_name, ayah):

    width = 900
    height = 650
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

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅ Oldingi", callback_data=f"surahpage_{page-1}")
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("➡ Keyingi", callback_data=f"surahpage_{page+1}")
        )

    if nav_buttons:
        kb.row(*nav_buttons)

    # 🔥 DOIMIY PASTKI QATOR
    kb.row(
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
    )

    return kb

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(
        InlineKeyboardButton("📖 Qur’on o‘qish", callback_data="quron_read"),
        InlineKeyboardButton("🎧 Zam suralar", callback_data="zam_menu"),
    )
    kb.add(
        InlineKeyboardButton("🌍 AI Translate", callback_data="ai_translate"),
        InlineKeyboardButton("🕌 Zikir ahlidan so‘rang", callback_data="zikir_ai"),
    )
    kb.add(
        InlineKeyboardButton("📚 Surani tanlash", callback_data="back_to_surah")
    )

    return kb



# ======================
# SEND AYAH
# ======================

async def send_ayah(user_id, message):

    user = get_user(user_id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

    # ===== AYAH DATA =====
    async with session.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-tajweed,uz.sodik"
    ) as resp:
        r = await resp.json()

    arabic_html = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']
    total_ayahs = r['data'][0]['surah']['numberOfAyahs']

    # ===== IMAGE =====
    create_card_image(arabic_html, uzbek, surah_name, ayah)
    await message.answer_photo(InputFile("card.png"))

    # ===== AUDIO (RAM орқали) =====
    sura = str(surah).zfill(3)
    ayah_num = str(ayah).zfill(3)
    audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

    async with session.get(audio_url) as audio_resp:
        if audio_resp.status == 200:
            import io
            audio_bytes = await audio_resp.read()

            await message.answer_audio(
                types.InputFile(
                    io.BytesIO(audio_bytes),
                    filename=f"{sura}{ayah_num}.mp3"
                )
            )
        else:
            await message.answer("🔊 Audio topilmadi.")

    # ===== NAVIGATION =====
kb = InlineKeyboardMarkup(row_width=3)

buttons = []

if ayah > 1:
    buttons.append(
        InlineKeyboardButton("⬅ Oldingi", callback_data="prev")
    )

if ayah < total_ayahs:
    buttons.append(
        InlineKeyboardButton("➡ Keyingi", callback_data="next")
    )

buttons.append(
    InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
)

kb.row(*buttons)

await message.answer("👇", reply_markup=kb)



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

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("🎙 Badr At-Turkiy", callback_data="zam_badr"))
    kb.add(InlineKeyboardButton("🎙 Mishary Alafasy", callback_data="zam_alafasy"))
    kb.add(InlineKeyboardButton("🎙 Shayx Alijon", callback_data="zam_alijon"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))

    await callback.message.edit_text("🎧 Qorini tanlang:", reply_markup=kb)
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("zam_"))
async def zam_play(callback: types.CallbackQuery):

    user = get_user(callback.from_user.id)
    surah = user["current_surah"]
    ayah = user["current_ayah"]

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
            await callback.message.answer("Audio topilmadi.")

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
    await message.answer("🏠 Bosh menyu:", reply_markup=main_menu())
   

async def show_ayah_page(callback, surah_number, page, total_ayahs):

    per_page = 50
    start = (page - 1) * per_page + 1
    end = min(start + per_page - 1, total_ayahs)

    kb = InlineKeyboardMarkup(row_width=6)

    for i in range(start, end + 1):
        kb.insert(
            InlineKeyboardButton(f"{i}-oyat", callback_data=f"ayah_{i}")
        )

    nav_buttons = []

    if start > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅ Oldingi 50", callback_data=f"ayahpage_{page-1}")
        )

    if end < total_ayahs:
        nav_buttons.append(
            InlineKeyboardButton("➡ Keyingi 50", callback_data=f"ayahpage_{page+1}")
        )

    if nav_buttons:
        kb.row(*nav_buttons)

    # 🔥 HAR DOIM KO‘RINADIGAN PASTKI QATOR
    kb.row(
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")
    )

    await callback.message.edit_text(
        "📜 Oyatni tanlang:",
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

    surah_id = int(callback.data.split("_")[1])

    update_user(callback.from_user.id, "current_surah", surah_id)
    update_user(callback.from_user.id, "current_ayah", 1)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_id}") as resp:
            r = await resp.json()

    total_ayahs = r['data']['numberOfAyahs']

    await show_ayah_page(callback, surah_id, 1, total_ayahs)



@dp.callback_query_handler(lambda c: c.data.startswith("ayahpage_"))
async def ayah_page(callback: types.CallbackQuery):

    page = int(callback.data.split("_")[1])

    user = get_user(callback.from_user.id)
    surah_number = user["current_surah"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah_number}") as resp:
            r = await resp.json()

    total_ayahs = r['data']['numberOfAyahs']

    await show_ayah_page(callback, surah_number, page, total_ayahs)

@dp.callback_query_handler(lambda c: c.data.startswith("ayah_"))
async def select_ayah(callback: types.CallbackQuery):

    ayah = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_ayah", ayah)

    await send_ayah(callback.from_user.id, callback.message)
    # 50 та диапазон аниқлаймиз

@dp.callback_query_handler(lambda c: c.data == "ai_translate")
async def enable_translate(callback: types.CallbackQuery):
    set_user_mode(callback.from_user.id, "translate")
    await callback.message.answer("🌍 Tarjima rejimi yoqildi. Matn yozing.")
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "zikir_ai")
async def enable_zikir(callback: types.CallbackQuery):
    set_user_mode(callback.from_user.id, "zikir")
    await callback.message.answer("🕌 Savolingizni yozing.")
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "back_to_surah")
async def back_to_surah(callback: types.CallbackQuery):
    set_user_mode(callback.from_user.id, "normal")
    await callback.message.edit_text(
        "📖 Surani tanlang:",
        reply_markup=surah_keyboard()
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
        await callback.message.edit_text(
            "🏠 Bosh menyu:",
            reply_markup=main_menu()
        )
        await callback.answer()
        return


    # ===== CACHE =====
    if surah not in SURAH_CACHE:
        async with session.get(f"https://api.alquran.cloud/v1/surah/{surah}") as resp:
            r = await resp.json()
            SURAH_CACHE[surah] = r['data']['numberOfAyahs']

    total_ayahs = SURAH_CACHE[surah]

    # ===== NEXT =====
    if callback.data == "next":
        if ayah < total_ayahs:
            update_user(user_id, "current_ayah", ayah + 1)

    # ===== PREV =====
    elif callback.data == "prev":
        if ayah > 1:
            update_user(user_id, "current_ayah", ayah - 1)

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
    session = aiohttp.ClientSession()
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
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)






