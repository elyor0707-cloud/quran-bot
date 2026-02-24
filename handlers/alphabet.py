"""
🔤 Arab alifbosi bo'limi
- 28 harf, 4 shakl
- Katta arabcha shrift
- Harakatlar va talaffuz
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

ALPHABET = [
    {"num": 1,  "ar": "أ", "name": "Alif",  "lat": "A",  "standalone": "أ", "begin": "أَ", "mid": "ـأ", "end": "ـأ", "harakat": "Fatha: أَ | Kasra: أِ | Damma: أُ | Sukun: أْ"},
    {"num": 2,  "ar": "ب", "name": "Bo",    "lat": "B",  "standalone": "ب", "begin": "بَـ","mid": "ـبـ","end": "ـب", "harakat": "Fatha: بَ | Kasra: بِ | Damma: بُ | Sukun: بْ"},
    {"num": 3,  "ar": "ت", "name": "To",    "lat": "T",  "standalone": "ت", "begin": "تَـ","mid": "ـتـ","end": "ـت", "harakat": "Fatha: تَ | Kasra: تِ | Damma: تُ | Sukun: تْ"},
    {"num": 4,  "ar": "ث", "name": "So",    "lat": "Th", "standalone": "ث", "begin": "ثَـ","mid": "ـثـ","end": "ـث", "harakat": "Fatha: ثَ | Kasra: ثِ | Damma: ثُ | Sukun: ثْ"},
    {"num": 5,  "ar": "ج", "name": "Jim",   "lat": "J",  "standalone": "ج", "begin": "جَـ","mid": "ـجـ","end": "ـج", "harakat": "Fatha: جَ | Kasra: جِ | Damma: جُ | Sukun: جْ"},
    {"num": 6,  "ar": "ح", "name": "Ho",    "lat": "Ḥ",  "standalone": "ح", "begin": "حَـ","mid": "ـحـ","end": "ـح", "harakat": "Fatha: حَ | Kasra: حِ | Damma: حُ | Sukun: حْ"},
    {"num": 7,  "ar": "خ", "name": "Xo",    "lat": "Kh", "standalone": "خ", "begin": "خَـ","mid": "ـخـ","end": "ـخ", "harakat": "Fatha: خَ | Kasra: خِ | Damma: خُ | Sukun: خْ"},
    {"num": 8,  "ar": "د", "name": "Dol",   "lat": "D",  "standalone": "د", "begin": "دَ", "mid": "ـد", "end": "ـد", "harakat": "Fatha: دَ | Kasra: دِ | Damma: دُ | Sukun: دْ"},
    {"num": 9,  "ar": "ذ", "name": "Zol",   "lat": "Dh", "standalone": "ذ", "begin": "ذَ", "mid": "ـذ", "end": "ـذ", "harakat": "Fatha: ذَ | Kasra: ذِ | Damma: ذُ | Sukun: ذْ"},
    {"num": 10, "ar": "ر", "name": "Ro",    "lat": "R",  "standalone": "ر", "begin": "رَ", "mid": "ـر", "end": "ـر", "harakat": "Fatha: رَ | Kasra: رِ | Damma: رُ | Sukun: رْ"},
    {"num": 11, "ar": "ز", "name": "Zayn",  "lat": "Z",  "standalone": "ز", "begin": "زَ", "mid": "ـز", "end": "ـز", "harakat": "Fatha: زَ | Kasra: زِ | Damma: زُ | Sukun: زْ"},
    {"num": 12, "ar": "س", "name": "Sin",   "lat": "S",  "standalone": "س", "begin": "سَـ","mid": "ـسـ","end": "ـس", "harakat": "Fatha: سَ | Kasra: سِ | Damma: سُ | Sukun: سْ"},
    {"num": 13, "ar": "ش", "name": "Shin",  "lat": "Sh", "standalone": "ش", "begin": "شَـ","mid": "ـشـ","end": "ـش", "harakat": "Fatha: شَ | Kasra: شِ | Damma: شُ | Sukun: شْ"},
    {"num": 14, "ar": "ص", "name": "Sod",   "lat": "Ṣ",  "standalone": "ص", "begin": "صَـ","mid": "ـصـ","end": "ـص", "harakat": "Fatha: صَ | Kasra: صِ | Damma: صُ | Sukun: صْ"},
    {"num": 15, "ar": "ض", "name": "Zod",   "lat": "Ḍ",  "standalone": "ض", "begin": "ضَـ","mid": "ـضـ","end": "ـض", "harakat": "Fatha: ضَ | Kasra: ضِ | Damma: ضُ | Sukun: ضْ"},
    {"num": 16, "ar": "ط", "name": "To",    "lat": "Ṭ",  "standalone": "ط", "begin": "طَـ","mid": "ـطـ","end": "ـط", "harakat": "Fatha: طَ | Kasra: طِ | Damma: طُ | Sukun: طْ"},
    {"num": 17, "ar": "ظ", "name": "Zo",    "lat": "Ẓ",  "standalone": "ظ", "begin": "ظَـ","mid": "ـظـ","end": "ـظ", "harakat": "Fatha: ظَ | Kasra: ظِ | Damma: ظُ | Sukun: ظْ"},
    {"num": 18, "ar": "ع", "name": "Ayn",   "lat": "'",  "standalone": "ع", "begin": "عَـ","mid": "ـعـ","end": "ـع", "harakat": "Fatha: عَ | Kasra: عِ | Damma: عُ | Sukun: عْ"},
    {"num": 19, "ar": "غ", "name": "Ghayn", "lat": "Gh", "standalone": "غ", "begin": "غَـ","mid": "ـغـ","end": "ـغ", "harakat": "Fatha: غَ | Kasra: غِ | Damma: غُ | Sukun: غْ"},
    {"num": 20, "ar": "ف", "name": "Fo",    "lat": "F",  "standalone": "ف", "begin": "فَـ","mid": "ـفـ","end": "ـف", "harakat": "Fatha: فَ | Kasra: فِ | Damma: فُ | Sukun: فْ"},
    {"num": 21, "ar": "ق", "name": "Qof",   "lat": "Q",  "standalone": "ق", "begin": "قَـ","mid": "ـقـ","end": "ـق", "harakat": "Fatha: قَ | Kasra: قِ | Damma: قُ | Sukun: قْ"},
    {"num": 22, "ar": "ك", "name": "Kof",   "lat": "K",  "standalone": "ك", "begin": "كَـ","mid": "ـكـ","end": "ـك", "harakat": "Fatha: كَ | Kasra: كِ | Damma: كُ | Sukun: كْ"},
    {"num": 23, "ar": "ل", "name": "Lom",   "lat": "L",  "standalone": "ل", "begin": "لَـ","mid": "ـلـ","end": "ـل", "harakat": "Fatha: لَ | Kasra: لِ | Damma: لُ | Sukun: لْ"},
    {"num": 24, "ar": "م", "name": "Mim",   "lat": "M",  "standalone": "م", "begin": "مَـ","mid": "ـمـ","end": "ـم", "harakat": "Fatha: مَ | Kasra: مِ | Damma: مُ | Sukun: مْ"},
    {"num": 25, "ar": "ن", "name": "Nun",   "lat": "N",  "standalone": "ن", "begin": "نَـ","mid": "ـنـ","end": "ـن", "harakat": "Fatha: نَ | Kasra: نِ | Damma: نُ | Sukun: نْ"},
    {"num": 26, "ar": "ه", "name": "Ho",    "lat": "H",  "standalone": "ه", "begin": "هَـ","mid": "ـهـ","end": "ـه", "harakat": "Fatha: هَ | Kasra: هِ | Damma: هُ | Sukun: هْ"},
    {"num": 27, "ar": "و", "name": "Vov",   "lat": "W/V","standalone": "و", "begin": "وَ", "mid": "ـو", "end": "ـو", "harakat": "Fatha: وَ | Kasra: وِ | Damma: وُ | Sukun: وْ"},
    {"num": 28, "ar": "ي", "name": "Yo",    "lat": "Y",  "standalone": "ي", "begin": "يَـ","mid": "ـيـ","end": "ـي", "harakat": "Fatha: يَ | Kasra: يِ | Damma: يُ | Sukun: يْ"},
]

def get_alphabet_list_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(0, len(ALPHABET), 4):
        row_letters = ALPHABET[i:i+4]
        for h in row_letters:
            builder.button(text=f"{h['ar']} {h['name']}", callback_data=f"alpha_{h['num']}")
    builder.adjust(4)
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(4, 4, 4, 4, 4, 4, 4, 1)
    return builder.as_markup()

def get_letter_keyboard(num: int):
    builder = InlineKeyboardBuilder()
    if num > 1:
        builder.button(text="⬅️ Oldingi", callback_data=f"alpha_{num-1}")
    if num < 28:
        builder.button(text="Keyingi ➡️", callback_data=f"alpha_{num+1}")
    builder.button(text="📋 Alifbo ro'yxati", callback_data="menu_alphabet")
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(2, 2)
    return builder.as_markup()

@router.callback_query(F.data == "menu_alphabet")
async def alphabet_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔤 <b>Arab alifbosi — 28 harf</b>\n\n"
        "Har bir harfni bosing — batafsil ma'lumot olasiz:\n"
        "• Katta arabcha ko'rinish\n"
        "• 4 xil shakl (boshi, o'rtasi, oxiri, alohida)\n"
        "• Harakatlar (fatha, kasra, damma, sukun)\n"
        "• Talaffuz",
        reply_markup=get_alphabet_list_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^alpha_(\d+)$"))
async def show_letter(callback: CallbackQuery):
    num = int(callback.data.split("_")[1])
    letter = next((l for l in ALPHABET if l["num"] == num), None)
    if not letter:
        await callback.answer("Harf topilmadi!")
        return

    text = (
        f"🔤 <b>{num}/28 — {letter['name']} ({letter['lat']})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Harfning katta ko'rinishi:</b>\n\n"
        f"<pre>    {letter['ar']}    </pre>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📐 4 xil shakli:</b>\n"
        f"• Alohida:     <code>{letter['standalone']}</code>\n"
        f"• So'z boshida: <code>{letter['begin']}</code>\n"
        f"• O'rtada:      <code>{letter['mid']}</code>\n"
        f"• Oxirida:      <code>{letter['end']}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>🎵 Harakatlar (Harakat):</b>\n"
        f"<code>{letter['harakat']}</code>\n\n"
        f"<b>🗣 Talaffuz:</b> [{letter['lat']}] — O'zbek tilidagi '{letter['name']}' harfiga o'xshash"
    )

    await callback.message.edit_text(text, reply_markup=get_letter_keyboard(num))
    await callback.answer()
