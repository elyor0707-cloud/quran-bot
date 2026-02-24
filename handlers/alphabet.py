from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.alphabet_data import ARABIC_ALPHABET, HARAKAT

router = Router()

def get_alphabet_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Barcha harflar", callback_data="alpha_list")
    builder.button(text="🎯 Harf o'rgan", callback_data="alpha_learn_1")
    builder.button(text="✍️ Harakatlar", callback_data="alpha_harakat")
    builder.button(text="🔗 Harf shakllari", callback_data="alpha_shapes")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

@router.callback_query(F.data == "menu_alphabet")
async def alphabet_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔤 <b>Arab alifbosi</b>\n\n"
        "Arab alifbosida <b>28 ta harf</b> mavjud.\n"
        "O'qish yo'nalishi: <b>o'ngdan chapga ⬅️</b>\n\n"
        "Nima o'rganmoqchisiz?",
        reply_markup=get_alphabet_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "alpha_list")
async def show_all_letters(callback: CallbackQuery):
    text = "📋 <b>28 ta arab harfi:</b>\n\n"
    
    for i, letter in enumerate(ARABIC_ALPHABET, 1):
        text += f"{i}. <b>{letter['letter']}</b> - {letter['name']} ({letter['transliteration']})\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Bitta harf o'rgan", callback_data="alpha_learn_1")
    builder.button(text="⬅️ Orqaga", callback_data="menu_alphabet")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("alpha_learn_"))
async def learn_letter(callback: CallbackQuery):
    letter_id = int(callback.data.split("_")[2])
    
    if letter_id < 1 or letter_id > 28:
        return
    
    letter = ARABIC_ALPHABET[letter_id - 1]
    
    # Misollar
    examples_text = ""
    for ex in letter['examples']:
        examples_text += f"  • {ex['word']} ({ex['transliteration']}) = {ex['meaning']}\n"
    
    text = (
        f"🔤 <b>Harf #{letter_id}/28</b>\n\n"
        f"<b>{'═' * 20}</b>\n"
        f"🌟 Harf: <b>{letter['letter']}</b>\n"
        f"📛 Nomi: <b>{letter['name']}</b>\n"
        f"🔊 Talaffuz: <b>{letter['transliteration']}</b>\n"
        f"<b>{'─' * 20}</b>\n\n"
        f"📐 <b>Shakllari:</b>\n"
        f"  Alohida: {letter['isolated']}\n"
        f"  Boshida: {letter['initial']}\n"
        f"  O'rtada: {letter['medial']}\n"
        f"  Oxirida: {letter['final']}\n\n"
        f"🔊 <b>Talaffuz:</b>\n  {letter['pronunciation']}\n\n"
        f"📚 <b>Misollar:</b>\n{examples_text}"
    )
    
    builder = InlineKeyboardBuilder()
    
    # Navigatsiya
    if letter_id > 1:
        builder.button(text="⬅️", callback_data=f"alpha_learn_{letter_id - 1}")
    
    builder.button(text=f"{letter_id}/28", callback_data="alpha_list")
    
    if letter_id < 28:
        builder.button(text="➡️", callback_data=f"alpha_learn_{letter_id + 1}")
    
    if letter_id > 1 and letter_id < 28:
        builder.adjust(3)
    else:
        builder.adjust(2)
    
    builder.button(text="⬅️ Alifbo menyusi", callback_data="menu_alphabet")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "alpha_harakat")
async def show_harakat(callback: CallbackQuery):
    text = "✨ <b>Harakatlar (belgilar)</b>\n\n"
    text += "Harakatlar harflar ustiga yoki ostiga qo'yiladigan belgilar bo'lib, harfning ovozini belgilaydi.\n\n"
    
    for key, h in HARAKAT.items():
        text += f"<b>{h['symbol']} {h['name']}</b>\n"
        text += f"  Ovoz: {h['sound']}\n"
        text += f"  Misol: {h['example']}\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Alifbo menyusi", callback_data="menu_alphabet")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "alpha_shapes")
async def show_letter_shapes(callback: CallbackQuery):
    text = "🔗 <b>Harflar 4 xil shaklda yoziladi:</b>\n\n"
    text += "Arab harflari so'zdagi o'rniga qarab shakli o'zgaradi:\n\n"
    text += "1️⃣ <b>Alohida</b> - so'z sifatida yoki yolg'iz\n"
    text += "2️⃣ <b>Boshida</b> - so'z boshida\n"
    text += "3️⃣ <b>O'rtada</b> - so'z o'rtasida\n"
    text += "4️⃣ <b>Oxirida</b> - so'z oxirida\n\n"
    text += "📌 <b>Misol (Ba harfi):</b>\n"
    text += "  ب - alohida\n"
    text += "  بـ - boshida\n"
    text += "  ـبـ - o'rtada\n"
    text += "  ـب - oxirida\n\n"
    text += "⚠️ <b>6 ta harf</b> faqat 2 shaklda (oldingi harfga birikmaydigan):\n"
    text += "ا د ذ ر ز و\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Harflarni ko'rish", callback_data="alpha_learn_1")
    builder.button(text="⬅️ Orqaga", callback_data="menu_alphabet")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
