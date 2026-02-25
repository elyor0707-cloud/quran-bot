from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()
InlineKeyboardButton("📖 Suralar", callback_data="suralar")
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔤 Arab alifbosi", callback_data="menu_alphabet")
    builder.button(text="📚 Arab grammatikasi", callback_data="menu_grammar")
    builder.button(text="📖 Tajvid kitobi", callback_data="menu_tajwid")
    builder.button(text="🎵 Qur'on audiolari", callback_data="menu_quran")
    builder.button(text="📗 Qur'on o'qish", callback_data="menu_quran_read")
    builder.button(text="✅ Test", callback_data="menu_test")
    builder.button(text="📊 Mening progressim", callback_data="menu_progress")
    builder.button(text="ℹ️ Bot haqida", callback_data="menu_about")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()

WELCOME_TEXT = (
    "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\n\n"
    "Assalomu alaykum, <b>{name}</b>! 🌙\n\n"
    "🕌 <b>Qur'on va Arab tili o'rganish botiga xush kelibsiz!</b>\n\n"
    "Bu bot orqali siz:\n"
    "• Arab harflarini o'rganasiz\n"
    "• Tajvid qoidalarini bilasiz\n"
    "• Qur'on suralarini tinglaysiz (Mishary Rashid)\n"
    "• Qur'on suralarini tajvidli o'qiysiz\n"
    "• Bilimingizni test orqali tekshirasiz\n"
    "• O'z progressingizni kuzatasiz\n\n"
    "Quyidan kerakli bo'limni tanlang 👇"
)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        WELCOME_TEXT.format(name=message.from_user.first_name),
        reply_markup=get_main_menu()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🕌 <b>Asosiy menyu</b>\n\nQuyidan kerakli bo'limni tanlang 👇",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "menu_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🕌 <b>Asosiy menyu</b>\n\nQuyidan kerakli bo'limni tanlang 👇",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_about")
async def about_bot(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")

    await callback.message.edit_text(
        "ℹ️ <b>Bot haqida</b>\n\n"
        "🕌 Bu bot arab tili va Qur'on o'rganish uchun yaratilgan\n\n"
        "<b>Imkoniyatlar:</b>\n"
        "• 28 ta arab harfi + harakatlar\n"
        "• Arab grammatikasi - bosqichma-bosqich\n"
        "• Tajvid qoidalari - batafsil\n"
        "• Qur'on suralari (Mishary Rashid al-Afasy)\n"
        "• Qur'on tajvidli o'qish bo'limi\n"
        "• Interaktiv testlar\n"
        "• Progress kuzatish\n\n"
        "<b>Qori:</b> Mishary Rashid al-Afasy 🎵\n\n"
        "Alloh ilmingizni ziyoda qilsin! 🤲",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
