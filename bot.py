from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
import os
import aiohttp
from database import get_surahs, get_user, update_user
from PIL import Image, ImageDraw, ImageFont
import textwrap

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# CARD IMAGE
# ======================

def create_card_image(arabic, uzbek, surah_name, ayah):

    width = 1200
    height = 900

    img = Image.new("RGB", (width, height), "#0f1b2d")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = (15, 27 + i//8, 45 + i//10)
        draw.line([(0, i), (width, i)], fill=color)

    arabic_font = ImageFont.truetype("Amiri-Regular.ttf", 90)
    uzbek_font = ImageFont.truetype("Amiri-Regular.ttf", 40)
    title_font = ImageFont.truetype("Amiri-Regular.ttf", 45)

    title = "Qur’oniy oyat"
    tw, th = draw.textsize(title, font=title_font)
    draw.text(((width - tw)/2, 40), title, fill="#d4af37", font=title_font)

    wrapped_ar = textwrap.fill(arabic, width=25)
    y = 200

    for line in wrapped_ar.split("\n"):
        w, h = draw.textsize(line, font=arabic_font)
        draw.text(((width - w)/2, y), line, fill="white", font=arabic_font)
        y += h + 25

    draw.line((200, y+20, width-200, y+20), fill="#d4af37", width=3)

    wrapped_uz = textwrap.fill(uzbek, width=60)
    y += 70

    for line in wrapped_uz.split("\n"):
        w, h = draw.textsize(line, font=uzbek_font)
        draw.text(((width - w)/2, y), line, fill="white", font=uzbek_font)
        y += h + 15

    footer = f"{surah_name} сураси, {ayah}-оят"
    fw, fh = draw.textsize(footer, font=title_font)
    draw.text(((width - fw)/2, height-100), footer, fill="#d4af37", font=title_font)

    img.save("card.png")

# ======================
# KEYBOARD
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
            f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,uz.sodik"
        ) as resp:
            r = await resp.json()

        arabic = r['data'][0]['text']
        uzbek = r['data'][1]['text']
        surah_name = r['data'][0]['surah']['englishName']
        total_ayahs = r['data'][0]['surah']['numberOfAyahs']

        create_card_image(arabic, uzbek, surah_name, ayah)
        await message.answer_photo(InputFile("card.png"))

        sura = str(surah).zfill(3)
        ayah_num = str(ayah).zfill(3)
        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_num}.mp3"

        async with session.get(audio_url) as audio_resp:
            if audio_resp.status == 200:
                filename = f"{sura}{ayah_num}.mp3"
                with open(filename, "wb") as f:
                    f.write(await audio_resp.read())
                await message.answer_audio(InputFile(filename))

    kb = InlineKeyboardMarkup()

    if ayah > 1:
        kb.insert(InlineKeyboardButton("⬅ Олдинги", callback_data="prev"))

    if ayah < total_ayahs:
        kb.insert(InlineKeyboardButton("➡ Кейинги", callback_data="next"))

    kb.add(InlineKeyboardButton("🏠 Бош меню", callback_data="menu"))

    await message.answer("👇 Навигация:", reply_markup=kb)

# ======================
# HANDLERS
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("📖 Сурани танланг:", reply_markup=surah_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
async def select_surah(callback: types.CallbackQuery):

    surah_number = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)

    await send_ayah(callback.from_user.id, callback.message)
    await callback.answer()@dp.callback_query_handler(lambda c: c.data.startswith("surah_"))
    async def select_surah(callback: types.CallbackQuery):

    await callback.answer()   # ⚡ Биринчи шу

    surah_number = int(callback.data.split("_")[1])
    update_user(callback.from_user.id, "current_surah", surah_number)
    update_user(callback.from_user.id, "current_ayah", 1)

    await send_ayah(callback.from_user.id, callback.message)


@dp.callback_query_handler(lambda c: c.data in ["next", "prev", "menu"])
async def navigation(callback: types.CallbackQuery):

    await callback.answer()   # ⚡ Биринчи жавоб

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
        return

    await send_ayah(user_id, callback.message)


# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
