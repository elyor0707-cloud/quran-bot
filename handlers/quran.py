from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Mishary Rashid Alafasy - ID: 1 (alafasy)
# API: https://api.alquran.cloud/v1/
QARI_ID = "ar.alafasy"
AUDIO_BASE_URL = "https://cdn.islamic.network/quran/audio/128/ar.alafasy"

# Barcha 114 sura
SURAHS = [
    (1, "Al-Fotiha", "الفاتحة", 7, "Makkiy"),
    (2, "Al-Baqara", "البقرة", 286, "Madiniy"),
    (3, "Ali Imron", "آل عمران", 200, "Madiniy"),
    (4, "An-Niso", "النساء", 176, "Madiniy"),
    (5, "Al-Moida", "المائدة", 120, "Madiniy"),
    (6, "Al-An'om", "الأنعام", 165, "Makkiy"),
    (7, "Al-A'rof", "الأعراف", 206, "Makkiy"),
    (8, "Al-Anfol", "الأنفال", 75, "Madiniy"),
    (9, "At-Tavba", "التوبة", 129, "Madiniy"),
    (10, "Yunus", "يونس", 109, "Makkiy"),
    (11, "Hud", "هود", 123, "Makkiy"),
    (12, "Yusuf", "يوسف", 111, "Makkiy"),
    (13, "Ar-Ra'd", "الرعد", 43, "Madiniy"),
    (14, "Ibrohim", "إبراهيم", 52, "Makkiy"),
    (15, "Al-Hijr", "الحجر", 99, "Makkiy"),
    (16, "An-Nahl", "النحل", 128, "Makkiy"),
    (17, "Al-Isro", "الإسراء", 111, "Makkiy"),
    (18, "Al-Kahf", "الكهف", 110, "Makkiy"),
    (19, "Maryam", "مريم", 98, "Makkiy"),
    (20, "Toha", "طه", 135, "Makkiy"),
    (21, "Al-Anbiyo", "الأنبياء", 112, "Makkiy"),
    (22, "Al-Hajj", "الحج", 78, "Madiniy"),
    (23, "Al-Mu'minun", "المؤمنون", 118, "Makkiy"),
    (24, "An-Nur", "النور", 64, "Madiniy"),
    (25, "Al-Furqon", "الفرقان", 77, "Makkiy"),
    (26, "Ash-Shuaro", "الشعراء", 227, "Makkiy"),
    (27, "An-Naml", "النمل", 93, "Makkiy"),
    (28, "Al-Qasas", "القصص", 88, "Makkiy"),
    (29, "Al-Ankabut", "العنكبوت", 69, "Makkiy"),
    (30, "Ar-Rum", "الروم", 60, "Makkiy"),
    (31, "Luqmon", "لقمان", 34, "Makkiy"),
    (32, "As-Sajda", "السجدة", 30, "Makkiy"),
    (33, "Al-Ahzob", "الأحزاب", 73, "Madiniy"),
    (34, "Sabo", "سبأ", 54, "Makkiy"),
    (35, "Fotir", "فاطر", 45, "Makkiy"),
    (36, "Yosin", "يس", 83, "Makkiy"),
    (37, "As-Soffot", "الصافات", 182, "Makkiy"),
    (38, "Sod", "ص", 88, "Makkiy"),
    (39, "Az-Zumar", "الزمر", 75, "Makkiy"),
    (40, "Gofir", "غافر", 85, "Makkiy"),
    (41, "Fussilat", "فصلت", 54, "Makkiy"),
    (42, "Ash-Shuro", "الشورى", 53, "Makkiy"),
    (43, "Az-Zukhruf", "الزخرف", 89, "Makkiy"),
    (44, "Ad-Duxon", "الدخان", 59, "Makkiy"),
    (45, "Al-Josiya", "الجاثية", 37, "Makkiy"),
    (46, "Al-Ahqof", "الأحقاف", 35, "Makkiy"),
    (47, "Muhammad", "محمد", 38, "Madiniy"),
    (48, "Al-Fath", "الفتح", 29, "Madiniy"),
    (49, "Al-Hujurot", "الحجرات", 18, "Madiniy"),
    (50, "Qof", "ق", 45, "Makkiy"),
    (51, "Az-Zoriyot", "الذاريات", 60, "Makkiy"),
    (52, "At-Tur", "الطور", 49, "Makkiy"),
    (53, "An-Najm", "النجم", 62, "Makkiy"),
    (54, "Al-Qamar", "القمر", 55, "Makkiy"),
    (55, "Ar-Rahman", "الرحمن", 78, "Madiniy"),
    (56, "Al-Voqia", "الواقعة", 96, "Makkiy"),
    (57, "Al-Hadid", "الحديد", 29, "Madiniy"),
    (58, "Al-Mujodala", "المجادلة", 22, "Madiniy"),
    (59, "Al-Hashr", "الحشر", 24, "Madiniy"),
    (60, "Al-Mumtahana", "الممتحنة", 13, "Madiniy"),
    (61, "As-Saff", "الصف", 14, "Madiniy"),
    (62, "Al-Juma", "الجمعة", 11, "Madiniy"),
    (63, "Al-Munofiqun", "المنافقون", 11, "Madiniy"),
    (64, "At-Tagobun", "التغابن", 18, "Madiniy"),
    (65, "At-Toloq", "الطلاق", 12, "Madiniy"),
    (66, "At-Tahrim", "التحريم", 12, "Madiniy"),
    (67, "Al-Mulk", "الملك", 30, "Makkiy"),
    (68, "Al-Qalam", "القلم", 52, "Makkiy"),
    (69, "Al-Hoqqo", "الحاقة", 52, "Makkiy"),
    (70, "Al-Ma'orij", "المعارج", 44, "Makkiy"),
    (71, "Nuh", "نوح", 28, "Makkiy"),
    (72, "Al-Jinn", "الجن", 28, "Makkiy"),
    (73, "Al-Muzzammil", "المزمل", 20, "Makkiy"),
    (74, "Al-Muddassir", "المدثر", 56, "Makkiy"),
    (75, "Al-Qiyoma", "القيامة", 40, "Makkiy"),
    (76, "Al-Inson", "الإنسان", 31, "Madiniy"),
    (77, "Al-Mursalot", "المرسلات", 50, "Makkiy"),
    (78, "An-Naba", "النبأ", 40, "Makkiy"),
    (79, "An-Noziot", "النازعات", 46, "Makkiy"),
    (80, "Abasa", "عبس", 42, "Makkiy"),
    (81, "At-Takwir", "التكوير", 29, "Makkiy"),
    (82, "Al-Infitor", "الانفطار", 19, "Makkiy"),
    (83, "Al-Mutaffifin", "المطففين", 36, "Makkiy"),
    (84, "Al-Inshiqoq", "الانشقاق", 25, "Makkiy"),
    (85, "Al-Buruj", "البروج", 22, "Makkiy"),
    (86, "At-Toriq", "الطارق", 17, "Makkiy"),
    (87, "Al-A'lo", "الأعلى", 19, "Makkiy"),
    (88, "Al-Goshiya", "الغاشية", 26, "Makkiy"),
    (89, "Al-Fajr", "الفجر", 30, "Makkiy"),
    (90, "Al-Balad", "البلد", 20, "Makkiy"),
    (91, "Ash-Shams", "الشمس", 15, "Makkiy"),
    (92, "Al-Layl", "الليل", 21, "Makkiy"),
    (93, "Ad-Duha", "الضحى", 11, "Makkiy"),
    (94, "Ash-Sharh", "الشرح", 8, "Makkiy"),
    (95, "At-Tin", "التين", 8, "Makkiy"),
    (96, "Al-Aloq", "العلق", 19, "Makkiy"),
    (97, "Al-Qadr", "القدر", 5, "Makkiy"),
    (98, "Al-Bayyina", "البينة", 8, "Madiniy"),
    (99, "Az-Zalzala", "الزلزلة", 8, "Madiniy"),
    (100, "Al-Odiyot", "العاديات", 11, "Makkiy"),
    (101, "Al-Qoria", "القارعة", 11, "Makkiy"),
    (102, "At-Takosur", "التكاثر", 8, "Makkiy"),
    (103, "Al-Asr", "العصر", 3, "Makkiy"),
    (104, "Al-Humaza", "الهمزة", 9, "Makkiy"),
    (105, "Al-Fil", "الفيل", 5, "Makkiy"),
    (106, "Quraysh", "قريش", 4, "Makkiy"),
    (107, "Al-Mooun", "الماعون", 7, "Makkiy"),
    (108, "Al-Kavsar", "الكوثر", 3, "Makkiy"),
    (109, "Al-Kofirun", "الكافرون", 6, "Makkiy"),
    (110, "An-Nasr", "النصر", 3, "Madiniy"),
    (111, "Al-Masad", "المسد", 5, "Makkiy"),
    (112, "Al-Ixlos", "الإخلاص", 4, "Makkiy"),
    (113, "Al-Falaq", "الفلق", 5, "Makkiy"),
    (114, "An-Nos", "الناس", 6, "Makkiy"),
]

def get_surah_list_page(page: int = 0):
    per_page = 10
    start = page * per_page
    end = min(start + per_page, len(SURAHS))
    
    builder = InlineKeyboardBuilder()
    
    for i in range(start, end):
        s = SURAHS[i]
        builder.button(
            text=f"{s[0]}. {s[1]} ({s[3]} oyat)",
            callback_data=f"surah_{s[0]}"
        )
    
    # Navigatsiya
    nav_buttons = []
    if page > 0:
        builder.button(text="⬅️ Oldingi", callback_data=f"surah_page_{page - 1}")
    
    builder.button(text=f"{page + 1}/{(len(SURAHS) - 1) // per_page + 1}", callback_data="menu_quran")
    
    if end < len(SURAHS):
        builder.button(text="Keyingi ➡️", callback_data=f"surah_page_{page + 1}")
    
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    
    builder.adjust(*([1] * (end - start)), 3, 1)
    
    return builder.as_markup()

@router.callback_query(F.data == "menu_quran")
async def quran_menu(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Suralar ro'yxati", callback_data="surah_page_0")
    builder.button(text="⭐ Mashhur suralar", callback_data="quran_popular")
    builder.button(text="🎵 Qori haqida", callback_data="quran_qari_info")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(2, 1, 1)
    
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari</b>\n\n"
        "🎤 <b>Qori:</b> Mishary Rashid al-Afasy\n"
        "📊 <b>Suralar soni:</b> 114\n\n"
        "Tinglashni xohlagan surani tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("surah_page_"))
async def surah_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    
    await callback.message.edit_text(
        "📖 <b>Suralar ro'yxati</b>\n\nSurani tanlang:",
        reply_markup=get_surah_list_page(page)
    )
    await callback.answer()

@router.callback_query(F.data == "quran_popular")
async def popular_surahs(callback: CallbackQuery):
    popular = [1, 2, 18, 36, 55, 56, 67, 78, 112, 113, 114]
    
    builder = InlineKeyboardBuilder()
    for num in popular:
        s = SURAHS[num - 1]
        builder.button(
            text=f"{s[0]}. {s[1]} - {s[2]}",
            callback_data=f"surah_{s[0]}"
        )
    builder.button(text="⬅️ Orqaga", callback_data="menu_quran")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "⭐ <b>Mashhur suralar:</b>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "quran_qari_info")
async def qari_info(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Orqaga", callback_data="menu_quran")
    
    await callback.message.edit_text(
        "🎤 <b>Mishary Rashid al-Afasy</b>\n\n"
        "📍 Vatan: Quvayt\n"
        "🎂 Tug'ilgan: 5-sentabr 1976\n\n"
        "Mishary Rashid al-Afasy — dunyodagi eng mashhur "
        "Qur'on qorilaridan biri. U o'zining nozik, go'zal va "
        "qalb tubiga yetadigan ovozi bilan jahon musulmonlarining "
        "yuragida chuqur o'rin egallagan.\n\n"
        "🏆 Ko'plab xalqaro Qur'on musobaqalari g'olibi\n"
        "🎵 100+ million muxlislar\n"
        "🕌 Imom va qori sifatida xizmat qiladi",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("surah_") and ~F.data.startswith("surah_page_"))
async def show_surah(callback: CallbackQuery, bot: Bot):
    try:
        surah_num = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        return
    
    surah = SURAHS[surah_num - 1]
    
    # Audio URL
    # Format: 001.mp3, 002.mp3, ...
    surah_str = str(surah_num).zfill(3)
    audio_url = f"https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/{surah_str}.mp3"
    
    builder = InlineKeyboardBuilder()
    
    if surah_num > 1:
        builder.button(text="⬅️", callback_data=f"surah_{surah_num - 1}")
    
    builder.button(text=f"{surah_num}/114", callback_data="surah_page_0")
    
    if surah_num < 114:
        builder.button(text="➡️", callback_data=f"surah_{surah_num + 1}")
    
    if surah_num > 1 and surah_num < 114:
        builder.adjust(3)
    else:
        builder.adjust(2)
    
    builder.button(text="⬅️ Suralar ro'yxati", callback_data="surah_page_0")
    builder.button(text="⬅️ Qur'on menyusi", callback_data="menu_quran")
    builder.adjust(*([3 if (surah_num > 1 and surah_num < 114) else 2]), 2)
    
    caption = (
        f"🎵 <b>{surah[0]}. {surah[1]}</b>\n"
        f"<i>{surah[2]}</i>\n\n"
        f"📊 Oyatlar: {surah[3]}\n"
        f"📍 Nozil bo'lgan joy: {surah[4]}\n"
        f"🎤 Qori: Mishary Rashid al-Afasy"
    )
    
    try:
        await callback.message.answer_audio(
            audio=URLInputFile(audio_url, filename=f"{surah[1]}.mp3"),
            caption=caption,
            reply_markup=builder.as_markup()
        )
        await callback.message.delete()
    except Exception:
        # Agar audio yuklanmasa - link berish
        builder2 = InlineKeyboardBuilder()
        builder2.button(text="🔗 Audio havolasi", url=audio_url)
        builder2.button(text="⬅️ Orqaga", callback_data="menu_quran")
        builder2.adjust(1)
        
        await callback.message.edit_text(
            f"{caption}\n\n"
            f"⚠️ Audio to'g'ridan-to'g'ri yuklash uchun pastdagi havolani bosing:",
            reply_markup=builder2.as_markup()
        )
    
    await callback.answer()
