import json
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher

# JSON юклаймиз
with open("quran.json", "r", encoding="utf-8") as f:
    QURAN = json.load(f)


# ==============================
# 4x4 SURA MENU
# ==============================
def sura_menu():
    kb = InlineKeyboardMarkup(row_width=4)
    buttons = []

    for sura in QURAN:
        buttons.append(
            InlineKeyboardButton(
                str(sura["id"]),
                callback_data=f"sura_{sura['id']}_1"
            )
        )

    kb.add(*buttons)
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    return kb


# ==============================
# AYAT NAVIGATION
# ==============================
def ayat_keyboard(sura_id, ayat_index, total_ayat):
    kb = InlineKeyboardMarkup(row_width=3)
    row = []

    if ayat_index > 1:
        row.append(
            InlineKeyboardButton("⬅️", callback_data=f"sura_{sura_id}_{ayat_index-1}")
        )

    row.append(
        InlineKeyboardButton("📖 Suralar", callback_data="suralar")
    )

    if ayat_index < total_ayat:
        row.append(
            InlineKeyboardButton("➡️", callback_data=f"sura_{sura_id}_{ayat_index+1}")
        )

    kb.row(*row)
    kb.add(InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu"))
    return kb


# ==============================
# SURA LIST HANDLER
# ==============================
async def show_suras(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📖 Suralar ro'yxati:",
        reply_markup=sura_menu()
    )
    await callback.answer()


# ==============================
# AYAT KO'RSATISH
# ==============================
async def show_ayat(callback: types.CallbackQuery):
    data = callback.data.split("_")
    sura_id = int(data[1])
    ayat_index = int(data[2])

    sura = next(s for s in QURAN if s["id"] == sura_id)
    ayat = sura["verses"][ayat_index - 1]
    total_ayat = len(sura["verses"])

    text = (
        f"📖 <b>{sura['name']} | {ayat_index}-oyat</b>\n\n"
        f"<b>{ayat['arabic']}</b>\n\n"
        f"<i>{ayat['latin']}</i>\n\n"
        f"<b>Tafsir:</b>\n{ayat['tafsir']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=ayat_keyboard(sura_id, ayat_index, total_ayat),
        parse_mode="HTML"
    )

    # AUDIO (INLINE PLAYER)
    audio_url = f"https://download.quranaudio.com/quran/mishaari_raashid_al_3afasee/{sura_id:03}.mp3"

    await callback.message.answer_audio(
        audio=audio_url,
        title=f"{sura['name']}",
        performer="Mishary Rashid al-Afasy"
    )

    await callback.answer()


# ==============================
# HANDLER REGISTER
# ==============================
def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_suras, lambda c: c.data == "suralar")
    dp.register_callback_query_handler(show_ayat, lambda c: c.data.startswith("sura_"))
