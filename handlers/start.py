from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import os

router = Router()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔤 Arab alifbosi", callback_data="menu_alphabet")
    builder.button(text="📚 Arab grammatikasi", callback_data="menu_grammar")
    builder.button(text="📖 Tajvid kitobi", callback_data="menu_tajwid")
    builder.button(text="🎵 Qur'on audiolari", callback_data="menu_quran")
    builder.button(text="✅ Test", callback_data="menu_test")
    builder.button(text="📊 Mening progressim", callback_data="menu_progress")
    builder.button(text="ℹ️ Bot haqida", callback_data="menu_about")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\n\n"
        f"Assalomu alaykum, <b>{user_name}</b>! 🌙\n\n"
        f"🕌 <b>Qur'on va Arab tili o'rganish botiga xush kelibsiz!</b>\n\n"
        f"Bu bot orqali siz:\n"
        f"• Arab harflarini o'rganasiz\n"
        f"• Tajvid qoidalarini bilasiz\n"
        f"• Qur'on suralarini tinglaysiz (Mishary Rashid)\n"
        f"• Bilimingizni test orqali tekshirasiz\n"
        f"• O'z progressingizni kuzatasiz\n\n"
        f"Quyidan kerakli bo'limni tanlang 👇",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "menu_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        f"🕌 <b>Asosiy menyu</b>\n\nQuyidan kerakli bo'limni tanlang 👇",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "menu_about")
async def about_bot(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Orqaga", callback_data="menu_main")
    
    await callback.message.edit_text(
        "ℹ️ <b>Bot haqida</b>\n\n"
        "🕌 Bu bot arab tili va Qur'on o'rganish uchun yaratilgan\n\n"
        "<b>Imkoniyatlar:</b>\n"
        "• 28 ta arab harfi + harakatlar\n"
        "• Arab grammatikasi - bosqichma-bosqich\n"
        "• Tajvid qoidalari - batafsil\n"
        "• Qur'on suralari (Mishary Rashid al-Afasy)\n"
        "• Interaktiv testlar\n"
        "• Progress kuzatish\n\n"
        "<b>Qori:</b> Mishary Rashid al-Afasy 🎵\n\n"
        "Alloh ilmingizni ziyoda qilsin! 🤲",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
