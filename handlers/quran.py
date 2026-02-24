"""
🎵 Qur'on audiolari — Mishary Rashid al-Afasy
- Audio + Arabcha matn + Lotin + Sharh
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# ============================================================
# SURALAR MA'LUMOTLARI
# ============================================================
SURAS = {
    1:   {"name": "Al-Fotiha",      "arabic": "الفاتحة",       "ayat": 7,   "page": 1},
    2:   {"name": "Al-Baqara",      "arabic": "البقرة",         "ayat": 286, "page": 1},
    3:   {"name": "Ali Imron",       "arabic": "آل عمران",       "ayat": 200, "page": 1},
    4:   {"name": "An-Niso",         "arabic": "النساء",         "ayat": 176, "page": 1},
    5:   {"name": "Al-Moida",        "arabic": "المائدة",        "ayat": 120, "page": 1},
    6:   {"name": "Al-An'om",        "arabic": "الأنعام",        "ayat": 165, "page": 1},
    7:   {"name": "Al-A'rof",        "arabic": "الأعراف",        "ayat": 206, "page": 1},
    8:   {"name": "Al-Anfol",        "arabic": "الأنفال",        "ayat": 75,  "page": 1},
    9:   {"name": "At-Tavba",        "arabic": "التوبة",         "ayat": 129, "page": 1},
    10:  {"name": "Yunus",           "arabic": "يونس",           "ayat": 109, "page": 1},
    36:  {"name": "Yosin",           "arabic": "يس",             "ayat": 83,  "page": 4},
    55:  {"name": "Ar-Rohman",       "arabic": "الرحمن",         "ayat": 78,  "page": 6},
    56:  {"name": "Al-Voqe'a",       "arabic": "الواقعة",        "ayat": 96,  "page": 6},
    67:  {"name": "Al-Mulk",         "arabic": "الملك",          "ayat": 30,  "page": 7},
    78:  {"name": "An-Naba",         "arabic": "النبأ",          "ayat": 40,  "page": 8},
    108: {"name": "Al-Kavsar",       "arabic": "الكوثر",         "ayat": 3,   "page": 11},
    112: {"name": "Al-Ixlos",        "arabic": "الإخلاص",        "ayat": 4,   "page": 11},
    113: {"name": "Al-Falaq",        "arabic": "الفلق",          "ayat": 5,   "page": 11},
    114: {"name": "An-Nas",          "arabic": "الناس",          "ayat": 6,   "page": 11},
}

# Sura basmalasi + 1-oyat (namunalar)
SURA_FIRST_AYAT = {
    1:   "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    36:  "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ يس",
    55:  "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ الرَّحْمَٰنُ",
    112: "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ قُلْ هُوَ اللَّهُ أَحَدٌ",
    113: "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
    114: "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
}

# Sura haqida qisqacha sharh
SURA_SHARH = {
    1:   "Fotiha — «Ochuvchi» demak. Bu sura Qur'onning kirish qismi bo'lib, namozda 17 marta o'qiladi. Shayx Muhammad Sodiq: «Fotiha — qisqa, lekin Qur'onning mohiyatini o'zida jamlagan.»",
    36:  "Yosin — Qur'on qalbi deb ataladi. Mishary Rashid al-Afasy ovozida bu surani eshitish ko'ngilni yumshatadi. Shayx Muhammad Sodiq: «Yosin — o'liklarning ro'parasida o'qiladi, chunki u oxirat haqida.»",
    55:  "Ar-Rohman — 31 marta «Rabbingizning qaysi ne'matini inkor etasiz?» oyati takrorlanadi. Shayx Muhammad Sodiq: «Bu sura shukr saboqidir.»",
    112: "Al-Ixlos — Qur'onning uchdan biriga teng. Allohning sof tavsifi. Shayx Muhammad Sodiq: «Bu surani 3 marta o'qish — butun Qur'on savobiga teng.»",
    113: "Al-Falaq — Himoya surasi. Shayx Muhammad Sodiq: «Uxlashdan oldin o'qing.»",
    114: "An-Nas — Vasvasdan himoya. Qur'onning oxirgi surasi. Shayx Muhammad Sodiq: «Allohga panoh so'rash — eng kuchli himoya.»",
}

PAGES_PER_PAGE = 10
TOTAL_SURAS = 114

def get_audio_url(sura_num: int) -> str:
    """Mishary Rashid al-Afasy audio URL"""
    return f"https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/{sura_num:03d}.mp3"

def get_sura_list_keyboard(page: int = 1):
    builder = InlineKeyboardBuilder()
    sura_nums = sorted(SURAS.keys())
    start = (page - 1) * PAGES_PER_PAGE
    end = start + PAGES_PER_PAGE
    page_suras = sura_nums[start:end]

    for num in page_suras:
        sura = SURAS[num]
        builder.button(
            text=f"🎵 {num}. {sura['name']} ({sura['arabic']})",
            callback_data=f"surah_{num}"
        )
    builder.adjust(1)

    nav = []
    if page > 1:
        nav.append(("⬅️ Oldingi", f"surah_page_{page-1}"))
    total_pages = (len(sura_nums) + PAGES_PER_PAGE - 1) // PAGES_PER_PAGE
    if page < total_pages:
        nav.append(("Keyingi ➡️", f"surah_page_{page+1}"))
    for text, cb in nav:
        builder.button(text=text, callback_data=cb)
    if nav:
        builder.adjust(1, len(nav))
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

def get_sura_back_keyboard(sura_num: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Suralar ro'yxati", callback_data="menu_quran")
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()

# ============================================================
# HANDLERS
# ============================================================
@router.callback_query(F.data == "menu_quran")
async def quran_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\n"
        "Quyidan sura tanlang — audio + arabcha matn + sharh beriladi 👇",
        reply_markup=get_sura_list_keyboard(1)
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^surah_page_(\d+)$"))
async def surah_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\n"
        "Quyidan sura tanlang 👇",
        reply_markup=get_sura_list_keyboard(page)
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^surah_(\d+)$"))
async def send_surah(callback: CallbackQuery):
    sura_num = int(callback.data.split("_")[1])
    sura = SURAS.get(sura_num)
    if not sura:
        await callback.answer("Sura topilmadi!", show_alert=True)
        return

    await callback.answer("Audio yuklanmoqda... ⏳")

    # Arabcha matn (birinchi oyat yoki umumiy)
    arabic_text = SURA_FIRST_AYAT.get(sura_num, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    sharh = SURA_SHARH.get(sura_num, f"{sura['name']} surasi — {sura['ayat']} oyat.")

    caption = (
        f"🎵 <b>{sura_num}. {sura['name']} — {sura['arabic']}</b>\n"
        f"({sura['ayat']} oyat) | Qori: Mishary Rashid al-Afasy\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📖 Arabcha matn:</b>\n\n"
        f"<pre>{arabic_text}</pre>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📚 Shayx Muhammad Sodiq sharhi:</b>\n"
        f"{sharh}"
    )

    audio_url = get_audio_url(sura_num)
    try:
        audio = URLInputFile(audio_url, filename=f"{sura['name']}.mp3")
        await callback.message.answer_audio(
            audio=audio,
            caption=caption,
            title=f"{sura_num}. {sura['name']} — {sura['arabic']}",
            performer="Mishary Rashid al-Afasy",
        )
    except Exception:
        # Agar audio yuklanmasa, matn bilan javob
        await callback.message.answer(
            caption + "\n\n🔗 Audio: " + audio_url,
            reply_markup=get_sura_back_keyboard(sura_num)
        )
        return

    await callback.message.answer(
        "Yuqoridagi audio haqida:",
        reply_markup=get_sura_back_keyboard(sura_num)
    )
