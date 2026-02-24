from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Oddiy in-memory progress (production'da database ishlating)
user_progress = {}

def get_user_stats(user_id: int) -> dict:
    if user_id not in user_progress:
        user_progress[user_id] = {
            "alphabet_learned": 0,
            "tajwid_learned": 0,
            "grammar_learned": 0,
            "tests_completed": 0,
            "total_correct": 0,
            "total_questions": 0,
            "surahs_listened": set(),
            "streak_days": 1,
        }
    return user_progress[user_id]

@router.callback_query(F.data == "menu_progress")
async def show_progress(callback: CallbackQuery):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    # Foizlar
    alpha_pct = min(100, (stats['alphabet_learned'] / 28) * 100)
    tajwid_pct = min(100, (stats['tajwid_learned'] / 8) * 100)
    grammar_pct = min(100, (stats['grammar_learned'] / 5) * 100)
    
    accuracy = 0
    if stats['total_questions'] > 0:
        accuracy = (stats['total_correct'] / stats['total_questions']) * 100
    
    def progress_bar(pct: float, length: int = 10) -> str:
        filled = int(pct / 100 * length)
        return "█" * filled + "░" * (length - filled)
    
    text = (
        f"📊 <b>Sizning progressingiz</b>\n\n"
        f"🔤 <b>Alifbo:</b>\n"
        f"  {progress_bar(alpha_pct)} {alpha_pct:.0f}%\n"
        f"  {stats['alphabet_learned']}/28 harf o'rganildi\n\n"
        f"📖 <b>Tajvid:</b>\n"
        f"  {progress_bar(tajwid_pct)} {tajwid_pct:.0f}%\n"
        f"  {stats['tajwid_learned']}/8 qoida o'rganildi\n\n"
        f"📚 <b>Grammatika:</b>\n"
        f"  {progress_bar(grammar_pct)} {grammar_pct:.0f}%\n"
        f"  {stats['grammar_learned']}/5 mavzu o'rganildi\n\n"
        f"🎵 <b>Tinglangan suralar:</b> {len(stats['surahs_listened'])}/114\n\n"
        f"✅ <b>Test natijalari:</b>\n"
        f"  Tugatilgan testlar: {stats['tests_completed']}\n"
        f"  To'g'rilik: {accuracy:.0f}%\n\n"
        f"🔥 <b>Kunlik streak:</b> {stats['streak_days']} kun\n\n"
        f"Davom eting! Alloh ilmingizni ziyoda qilsin! 🤲"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔤 Alifboni o'rganish", callback_data="menu_alphabet")
    builder.button(text="📖 Tajvidni o'rganish", callback_data="menu_tajwid")
    builder.button(text="✅ Test topshirish", callback_data="menu_test")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(2, 1, 1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
