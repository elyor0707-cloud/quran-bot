from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.tajwid_data import TAJWID_RULES, WAQF_SIGNS

router = Router()

@router.callback_query(F.data == "menu_tajwid")
async def tajwid_menu(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    # Kategoriyalar
    builder.button(text="🟢 Nun sakin qoidalari", callback_data="tajwid_cat_nun")
    builder.button(text="🔵 Madd qoidalari", callback_data="tajwid_cat_madd")
    builder.button(text="🔴 Gunna va Qalqala", callback_data="tajwid_cat_gunna")
    builder.button(text="⭐ Lam qoidalari", callback_data="tajwid_cat_lam")
    builder.button(text="📋 Vaqf belgilari", callback_data="tajwid_waqf")
    builder.button(text="📚 Barcha qoidalar", callback_data="tajwid_all")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(2, 2, 2, 1)
    
    await callback.message.edit_text(
        "📖 <b>Tajvid kitobi</b>\n\n"
        "Tajvid — Qur'onni to'g'ri va go'zal o'qish qoidalari ilmi.\n\n"
        "🏆 <b>Qoidalar soni:</b> {}\n\n"
        "Qaysi bo'limni o'rganmoqchisiz?".format(len(TAJWID_RULES)),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "tajwid_all")
async def tajwid_all(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    for rule in TAJWID_RULES:
        builder.button(
            text=f"{rule['color']} {rule['name']}",
            callback_data=f"tajwid_rule_{rule['id']}"
        )
    
    builder.button(text="⬅️ Orqaga", callback_data="menu_tajwid")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "📚 <b>Barcha tajvid qoidalari:</b>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tajwid_cat_"))
async def tajwid_category(callback: CallbackQuery):
    cat = callback.data.split("_")[2]
    
    cat_map = {
        "nun": "Nun sakin va tanvin qoidalari",
        "madd": "Madd qoidalari",
        "gunna": "Harflar xususiyatlari",
        "lam": "Lam qoidalari",
    }
    
    cat_name = cat_map.get(cat, "")
    filtered = [r for r in TAJWID_RULES if r['category'] == cat_name]
    
    builder = InlineKeyboardBuilder()
    for rule in filtered:
        builder.button(
            text=f"{rule['color']} {rule['name']}",
            callback_data=f"tajwid_rule_{rule['id']}"
        )
    builder.button(text="⬅️ Orqaga", callback_data="menu_tajwid")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"📖 <b>{cat_name}</b>\n\nQoidani tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tajwid_rule_"))
async def show_tajwid_rule(callback: CallbackQuery):
    rule_id = int(callback.data.split("_")[2])
    rule = next((r for r in TAJWID_RULES if r['id'] == rule_id), None)
    
    if not rule:
        return
    
    # Asosiy matn
    text = (
        f"{rule['color']} <b>{rule['name']}</b>\n"
        f"<i>({rule['arabic']})</i>\n\n"
        f"📂 <b>Kategoriya:</b> {rule['category']}\n\n"
        f"📝 <b>Ta'rif:</b>\n{rule['description']}\n\n"
    )
    
    # Harflar
    if 'letters' in rule and rule['letters']:
        text += f"🔤 <b>Harflar:</b> {' '.join(rule['letters'])}\n\n"
    
    # Misol
    if 'example_arabic' in rule:
        text += (
            f"📌 <b>Misol:</b>\n"
            f"  {rule['example_arabic']}\n"
            f"  ({rule.get('example_transliteration', '')})\n"
            f"  = {rule.get('example_meaning', '')}\n\n"
        )
    
    # Maslahat
    if 'tip' in rule:
        text += f"{rule['tip']}"
    
    # Qoidalar navigatsiyasi
    builder = InlineKeyboardBuilder()
    if rule_id > 1:
        builder.button(text="⬅️", callback_data=f"tajwid_rule_{rule_id - 1}")
    
    builder.button(text=f"{rule_id}/{len(TAJWID_RULES)}", callback_data="tajwid_all")
    
    if rule_id < len(TAJWID_RULES):
        builder.button(text="➡️", callback_data=f"tajwid_rule_{rule_id + 1}")
    
    if rule_id > 1 and rule_id < len(TAJWID_RULES):
        builder.adjust(3)
    else:
        builder.adjust(2)
    
    builder.button(text="⬅️ Tajvid menyusi", callback_data="menu_tajwid")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "tajwid_waqf")
async def show_waqf(callback: CallbackQuery):
    text = "🛑 <b>Vaqf belgilari</b>\n\n"
    text += "Vaqf — Qur'on o'qishda to'xtatish belgilari:\n\n"
    
    for w in WAQF_SIGNS:
        text += f"<b>{w['sign']}</b> — {w['name']}\n  {w['description']}\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Tajvid menyusi", callback_data="menu_tajwid")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
