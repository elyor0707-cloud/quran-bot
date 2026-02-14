import requests
import sqlite3
import os
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

current_letter = {}

# ======================
# ARABIC LETTERS DATA
# ======================

arabic_letters = [
{"letter":"ا","name":"Алиф","pronunciation":"А товуши","reading":"а","begin":"ا","middle":"ـا","end":"ـا","example":"اللّٰه","audio":"letters_audio/alif.mp3"},
{"letter":"ب","name":"Ба","pronunciation":"Б товуши","reading":"б","begin":"بـ","middle":"ـبـ","end":"ـب","example":"بسم","audio":"letters_audio/ba.mp3"},
{"letter":"ت","name":"Та","pronunciation":"Т товуши","reading":"т","begin":"تـ","middle":"ـتـ","end":"ـت","example":"توبة","audio":"letters_audio/ta.mp3"},
{"letter":"ث","name":"Са","pronunciation":"С (th)","reading":"с","begin":"ثـ","middle":"ـثـ","end":"ـث","example":"ثواب","audio":"letters_audio/tha.mp3"},
{"letter":"ج","name":"Жим","pronunciation":"Ж","reading":"ж","begin":"جـ","middle":"ـجـ","end":"ـج","example":"جنة","audio":"letters_audio/jeem.mp3"},
{"letter":"ح","name":"Ҳа","pronunciation":"Ҳ қаттиқ","reading":"ҳ","begin":"حـ","middle":"ـحـ","end":"ـح","example":"حق","audio":"letters_audio/ha.mp3"},
{"letter":"خ","name":"Хо","pronunciation":"Х","reading":"х","begin":"خـ","middle":"ـخـ","end":"ـخ","example":"خلق","audio":"letters_audio/kha.mp3"},
{"letter":"د","name":"Дал","pronunciation":"Д","reading":"д","begin":"د","middle":"ـد","end":"ـد","example":"دين","audio":"letters_audio/dal.mp3"},
{"letter":"ذ","name":"Зал","pronunciation":"З (dh)","reading":"з","begin":"ذ","middle":"ـذ","end":"ـذ","example":"ذكر","audio":"letters_audio/dhal.mp3"},
{"letter":"ر","name":"Ро","pronunciation":"Р","reading":"р","begin":"ر","middle":"ـر","end":"ـر","example":"رحمن","audio":"letters_audio/ra.mp3"},
{"letter":"ز","name":"Зай","pronunciation":"З","reading":"з","begin":"ز","middle":"ـز","end":"ـز","example":"زكاة","audio":"letters_audio/zay.mp3"},
{"letter":"س","name":"Син","pronunciation":"С","reading":"с","begin":"سـ","middle":"ـسـ","end":"ـس","example":"سلام","audio":"letters_audio/seen.mp3"},
{"letter":"ش","name":"Шин","pronunciation":"Ш","reading":"ш","begin":"شـ","middle":"ـشـ","end":"ـش","example":"شمس","audio":"letters_audio/sheen.mp3"},
{"letter":"ص","name":"Сод","pronunciation":"Қаттиқ С","reading":"с","begin":"صـ","middle":"ـصـ","end":"ـص","example":"صلاة","audio":"letters_audio/sad.mp3"},
{"letter":"ض","name":"Дод","pronunciation":"Қаттиқ Д","reading":"д","begin":"ضـ","middle":"ـضـ","end":"ـض","example":"ضلال","audio":"letters_audio/dad.mp3"},
{"letter":"ط","name":"То","pronunciation":"Қаттиқ Т","reading":"т","begin":"طـ","middle":"ـطـ","end":"ـط","example":"طاعة","audio":"letters_audio/ta2.mp3"},
{"letter":"ظ","name":"Зо","pronunciation":"Қаттиқ З","reading":"з","begin":"ظـ","middle":"ـظـ","end":"ـظ","example":"ظلم","audio":"letters_audio/za.mp3"},
{"letter":"ع","name":"Айн","pronunciation":"Томоқ товуш","reading":"ъ","begin":"عـ","middle":"ـعـ","end":"ـع","example":"علم","audio":"letters_audio/ain.mp3"},
{"letter":"غ","name":"Ғайн","pronunciation":"Ғ","reading":"ғ","begin":"غـ","middle":"ـغـ","end":"ـغ","example":"غفور","audio":"letters_audio/ghain.mp3"},
{"letter":"ف","name":"Фа","pronunciation":"Ф","reading":"ф","begin":"فـ","middle":"ـفـ","end":"ـف","example":"فجر","audio":"letters_audio/fa.mp3"},
{"letter":"ق","name":"Қоф","pronunciation":"Қ","reading":"қ","begin":"قـ","middle":"ـقـ","end":"ـق","example":"قرآن","audio":"letters_audio/qaf.mp3"},
{"letter":"ك","name":"Каф","pronunciation":"К","reading":"к","begin":"كـ","middle":"ـكـ","end":"ـك","example":"كتاب","audio":"letters_audio/kaf.mp3"},
{"letter":"ل","name":"Лам","pronunciation":"Л","reading":"л","begin":"لـ","middle":"ـلـ","end":"ـل","example":"الله","audio":"letters_audio/lam.mp3"},
{"letter":"م","name":"Мим","pronunciation":"М","reading":"м","begin":"مـ","middle":"ـمـ","end":"ـم","example":"ملك","audio":"letters_audio/meem.mp3"},
{"letter":"ن","name":"Нун","pronunciation":"Н","reading":"н","begin":"نـ","middle":"ـنـ","end":"ـن","example":"نور","audio":"letters_audio/noon.mp3"},
{"letter":"ه","name":"Ҳа","pronunciation":"Ҳ енгил","reading":"ҳ","begin":"هـ","middle":"ـهـ","end":"ـه","example":"هدى","audio":"letters_audio/ha2.mp3"},
{"letter":"و","name":"Вов","pronunciation":"В/У","reading":"в","begin":"و","middle":"ـو","end":"ـو","example":"وعد","audio":"letters_audio/waw.mp3"},
{"letter":"ي","name":"Йа","pronunciation":"Й","reading":"й","begin":"يـ","middle":"ـيـ","end":"ـي","example":"يوم","audio":"letters_audio/ya.mp3"}
]

# ======================
# MAIN MENUrd=True)
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("📖 Бугунги оят")
main_keyboard.add("📘 Араб алифбоси")
main_keyboard.add("📚 Грамматика")
main_keyboard.add("💎 Premium")

# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboa
main_keyboard.add("📘 Араб алифбоси")

# ======================
# LETTER KEYBOARD
# ======================

def letter_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⬅ Олдинги ҳарф", "➡ Кейинги ҳарф")
    kb.add("🔊 Талаффуз аудио")
    kb.add("🏠 Уйга қайтиш")
    return kb

# ======================
# START
# ======================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Ассалому алайкум!", reply_markup=main_keyboard)

# ======================
# ARABIC ALPHABET START
# ======================

@dp.message_handler(lambda m: m.text == "📘 Араб алифбоси")
async def arabic_start(message: types.Message):
    current_letter[message.from_user.id] = 0
    await send_letter(message, 0)

# ======================
# SEND LETTER FUNCTION
# ======================

async def send_letter(message, index):
    letter = arabic_letters[index]

    text = f"""
📘 Ҳарф: {letter['letter']}

🔤 Номи: {letter['name']}
🗣 Талаффуз: {letter['pronunciation']}
📖 Ўқилиши: {letter['reading']}

📌 Сўз бошида: {letter['begin']}
📌 Сўз ўртасида: {letter['middle']}
📌 Сўз охирида: {letter['end']}

🕌 Қуръондан мисол: {letter['example']}
"""

    await message.answer(text, reply_markup=letter_keyboard())

# ======================
# NEXT LETTER
# ======================

@dp.message_handler(lambda m: m.text == "➡ Кейинги ҳарф")
async def next_letter(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0) + 1

    if index >= len(arabic_letters):
        await message.answer("🎉 Алифбо тугади!", reply_markup=main_keyboard)
        return

    current_letter[user_id] = index
    await send_letter(message, index)

# ======================
# PREVIOUS LETTER
# ======================

@dp.message_handler(lambda m: m.text == "⬅ Олдинги ҳарф")
async def prev_letter(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0) - 1

    if index < 0:
        index = 0

    current_letter[user_id] = index
    await send_letter(message, index)

# ======================
# LETTER AUDIO
# ======================

@dp.message_handler(lambda m: m.text == "🔊 Талаффуз аудио")
async def letter_audio(message: types.Message):
    user_id = message.from_user.id
    index = current_letter.get(user_id, 0)

    letter = arabic_letters[index]

    if os.path.exists(letter["audio"]):
        with open(letter["audio"], "rb") as audio:
            await message.answer_audio(audio)
    else:
        await message.answer("Аудио файл топилмади.")

# ======================
# HOME
# ======================

@dp.message_handler(lambda m: m.text == "🏠 Уйга қайтиш")
async def go_home(message: types.Message):
    await message.answer("Бош меню", reply_markup=main_keyboard)

# ======================
# TODAY AYAH
# ======================

@dp.message_handler(lambda m: m.text == "📖 Бугунги оят")
async def today_ayah(message: types.Message):

    today = datetime.now().date()
    start_date = datetime(2026, 1, 1).date()

    days_passed = (today - start_date).days
    start_index = days_passed * 5 + 1
    end_index = start_index + 5

    for i in range(start_index, end_index):

        response = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{i}/editions/quran-uthmani,uz.sodik"
        )
        data = response.json()

        arabic = data['data'][0]['text']
        uzbek = data['data'][1]['text']

        await message.answer(f"{i}-оят")
        await message.answer(arabic)
        await message.answer(uzbek)

        # 🎧 Мишарий аудио қайтариш
        sura = str(data['data'][0]['surah']['number']).zfill(3)
        ayah_number = str(data['data'][0]['numberInSurah']).zfill(3)

        audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{sura}{ayah_number}.mp3"

        await message.answer_audio(audio_url)


# ======================
# RUN
# ======================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
