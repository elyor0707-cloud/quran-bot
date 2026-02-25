"""
🎵 Qur'on audiolari — 1-rasmdagi uslubda
- Chiroyli karta (rasm): arabcha katta + lotin + tafsir
- Audio alohida
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

router = Router()

# ============================================================
# SURALAR
# ============================================================
SURAS = {
    1: {
        "name": "Al-Fotiha", "arabic": "الفاتحة", "ayat": 7,
        "ar": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
        "lat": "Bismillāhir-raḥmānir-raḥīm",
        "tafsir": "Fotiha — «Ochuvchi» demak. Bu sura Qur'onning kirish qismi bo'lib, namozda 17 marta o'qiladi. Shayx Muhammad Sodiq: «Fotiha — qisqa, lekin Qur'onning mohiyatini o'zida jamlagan. Bu surani chuqur tushungan odam Islomning mohiyatini tushungan.»"
    },
    2: {
        "name": "Al-Baqara", "arabic": "البقرة", "ayat": 286,
        "ar": "الٓمٓ",
        "lat": "Alif-Laam-Miim",
        "tafsir": "Al-Baqara — «Sigir» surasi. Qur'onning eng uzun surasi (286 oyat). Shayx Muhammad Sodiq: «Uyingizda muntazam o'qilsa, shayton kirmaydi. Unda islom hayotining barcha sohalari — ibodat, muomala, oila, huquq — bayon etilgan.»"
    },
    3: {
        "name": "Ali Imron", "arabic": "آل عمران", "ayat": 200,
        "ar": "الٓمٓ",
        "lat": "Alif-Laam-Miim",
        "tafsir": "Ali Imron — Imron oilasi. 200 oyat. Shayx Muhammad Sodiq: «Bu sura xristianlar bilan munosabat, Iso alayhissalom haqiqati va mo'minlar xususiyatlarini bayon etadi.»"
    },
    4: {
        "name": "An-Niso", "arabic": "النساء", "ayat": 176,
        "ar": "يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ",
        "lat": "Yā ayyuhan-nāsut-taqū rabbakum",
        "tafsir": "An-Niso — Ayollar surasi. 176 oyat. Shayx Muhammad Sodiq: «Bu surada meros, nikoh, ayollar huquqlari, urush va sulh haqida batafsil ko'rsatmalar berilgan.»"
    },
    5: {
        "name": "Al-Moida", "arabic": "المائدة", "ayat": 120,
        "ar": "يَا أَيُّهَا الَّذِينَ آمَنُوا أَوْفُوا بِالْعُقُودِ",
        "lat": "Yā ayyuhal-ladhīna āmanū awfū bil-'uqūd",
        "tafsir": "Al-Moida — Dasturxon. 120 oyat. Shayx Muhammad Sodiq: «Bu Qur'onning so'nggi nozil bo'lgan suralari. Halol-harom ovqatlar, ahd-pakt va adolat qoidalari bayon etilgan.»"
    },
    36: {
        "name": "Yosin", "arabic": "يس", "ayat": 83,
        "ar": "يسٓ",
        "lat": "Yaa-Siin",
        "tafsir": "Yosin — Qur'on qalbi. 83 oyat. Shayx Muhammad Sodiq: «Bu surani har kuni o'qish katta savob. O'liklar huzurida o'qiladi — chunki Qiyomat, tirilish va oxirat haqida. Mishary Rashid ovozida eshitish yurakni yumshatadi.»"
    },
    55: {
        "name": "Ar-Rohman", "arabic": "الرحمن", "ayat": 78,
        "ar": "الرَّحْمَنُ",
        "lat": "Ar-Raḥmān",
        "tafsir": "Ar-Rohman — Rahman (Mehribon). 78 oyat. Shayx Muhammad Sodiq: «Bu surada 31 marta «Rabbingizning qaysi ne'matini inkor etasiz?» takrorlanadi — har marta yangi ne'mat eslatiladi. Bu sura shukr darsligidir.»"
    },
    56: {
        "name": "Al-Voqe'a", "arabic": "الواقعة", "ayat": 96,
        "ar": "إِذَا وَقَعَتِ الْوَاقِعَةُ",
        "lat": "Idhā waqa'atil-wāqi'ah",
        "tafsir": "Al-Voqe'a — Voqea (Qiyomat). 96 oyat. Shayx Muhammad Sodiq: «Har kecha o'qilsa — faqirlikdan himoya. Bu surada odamlar uch guruhga bo'linishi batafsil bayon etilgan.»"
    },
    67: {
        "name": "Al-Mulk", "arabic": "الملك", "ayat": 30,
        "ar": "تَبَارَكَ الَّذِي بِيَدِهِ الْمُلْكُ",
        "lat": "Tabārakal-ladhī biyadihil-mulk",
        "tafsir": "Al-Mulk — Saltanat. 30 oyat. Shayx Muhammad Sodiq: «Bu surani har kecha uxlashdan oldin o'qing — qabr azobidan himoya. Payg'ambar (s.a.v.) uni hech qachon tark etmaganlar.»"
    },
    78: {
        "name": "An-Naba", "arabic": "النبأ", "ayat": 40,
        "ar": "عَمَّ يَتَسَاءَلُونَ",
        "lat": "'Amma yatasā'alūn",
        "tafsir": "An-Naba — Ulug' xabar. 40 oyat. Shayx Muhammad Sodiq: «Bu sura Qiyomat kuni va uning belgilari haqida. Kichik suralarga kiradi, ammo savob katta.»"
    },
    108: {
        "name": "Al-Kavsar", "arabic": "الكوثر", "ayat": 3,
        "ar": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
        "lat": "Innā a'ṭaynākal-kawṯar",
        "tafsir": "Al-Kavsar — Ko'payish. 3 oyat — Qur'onning eng qisqa surasi. Shayx Muhammad Sodiq: «Kavsar — jannatdagi havuz va Payg'ambarga berilgan barcha ne'mat. Bu sura dushmanlarni xo'rlashni bashorat qilgan.»"
    },
    112: {
        "name": "Al-Ixlos", "arabic": "الإخلاص", "ayat": 4,
        "ar": "قُلْ هُوَ اللَّهُ أَحَدٌ",
        "lat": "Qul huwallāhu aḥad",
        "tafsir": "Al-Ixlos — Xolislik. 4 oyat. Shayx Muhammad Sodiq: «Bu sura Qur'onning uchdan biriga teng — Allohning zotini to'liq bayon etadi. Har kuni 3 marta o'qish — Qur'onni bir marta o'qigandek.»"
    },
    113: {
        "name": "Al-Falaq", "arabic": "الفلق", "ayat": 5,
        "ar": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
        "lat": "Qul a'ūdhu bi-rabbil-falaq",
        "tafsir": "Al-Falaq — Tong. 5 oyat. Shayx Muhammad Sodiq: «Bu sura — panoh surasi. Uxlashdan oldin o'qing. Mehr, sehr, hasad va kecha yovuzliklaridan himoya.»"
    },
    114: {
        "name": "An-Nas", "arabic": "الناس", "ayat": 6,
        "ar": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
        "lat": "Qul a'ūdhu bi-rabbin-nās",
        "tafsir": "An-Nas — Odamlar. 6 oyat — Qur'onning oxirgi surasi. Shayx Muhammad Sodiq: «Allohga uch sifat — Rabb, Malik, Ilohi — bilan murojaat etiladi. Har kecha uxlashdan oldin o'qing.»"
    },
}

PAGES_PER_PAGE = 8

# ============================================================
# KARTA YARATISH — 1-rasmdagi uslub
# ============================================================
def create_quran_card(sura_num: int, sura: dict) -> bytes:
    W, H = 800, 620

    # Gradient fon (to'q yashil)
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(15 + ratio * 18)
        g = int(62 + ratio * 38)
        b = int(42 + ratio * 22)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Bezak doiralar
    draw.ellipse([(-70, -70), (190, 190)], fill=(28, 88, 58))
    draw.ellipse([(630, 450), (900, 720)], fill=(18, 72, 50))
    draw.ellipse([(660, -55), (850, 135)], fill=(23, 80, 54))
    draw.ellipse([(30, 490), (185, 645)], fill=(16, 68, 46))

    GOLD  = (255, 212, 75)
    WHITE = (255, 255, 255)
    LIGHT = (192, 226, 205)
    LINE  = (75, 142, 102)

    # Fontlar
    SERIF  = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"   # arabcha
    SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def f(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    fh  = f(SANS_B, 20)   # header
    far = f(SERIF, 54)    # arabic
    fla = f(SANS,  22)    # latin
    flb = f(SANS_B, 17)   # label
    ftx = f(SANS,  15)    # tafsir
    fft = f(SANS_B, 18)   # footer

    def cx(text, font):
        try:
            b = draw.textbbox((0,0), text, font=font)
            return (W - (b[2]-b[0])) // 2
        except Exception:
            return 100

    # ── SARLAVHA ──
    header = "Qur'oniy oyat"
    draw.text((cx(header, fh), 22), header, font=fh, fill=GOLD)
    draw.line([(70, 56), (W-70, 56)], fill=GOLD, width=1)

    # ── ARABCHA ──
    ar = sura["ar"]
    draw.text((cx(ar, far), 72), ar, font=far, fill=WHITE)

    # ── LOTINCHA ──
    lat = sura["lat"]
    draw.text((cx(lat, fla), 150), lat, font=fla, fill=GOLD)

    draw.line([(70, 188), (W-70, 188)], fill=LINE, width=1)

    # ── TAFSIR ──
    draw.text((60, 200), "📖  Tafsir:", font=flb, fill=GOLD)
    wrapped = textwrap.wrap(sura["tafsir"], width=75)
    y_t = 228
    for line in wrapped:
        if y_t > 510:
            draw.text((60, y_t), "...", font=ftx, fill=LIGHT)
            break
        draw.text((60, y_t), line, font=ftx, fill=LIGHT)
        y_t += 21

    draw.line([(70, 530), (W-70, 530)], fill=LINE, width=1)

    # ── PASTKI SARLAVHA ──
    footer = f"{sura['name']} surasi  |  1-oyat"
    draw.text((cx(footer, fft), 544), footer, font=fft, fill=GOLD)
    draw.line([(70, 578), (W-70, 578)], fill=GOLD, width=1)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=94)
    buf.seek(0)
    return buf.read()


def get_audio_url(sura_num: int) -> str:
    return f"https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/{sura_num:03d}.mp3"

def get_sura_list_keyboard(page: int = 1):
    builder = InlineKeyboardBuilder()
    sura_nums = sorted(SURAS.keys())
    start = (page-1) * PAGES_PER_PAGE
    for num in sura_nums[start:start+PAGES_PER_PAGE]:
        s = SURAS[num]
        builder.button(
            text=f"🎵 {num}. {s['name']} ({s['arabic']})",
            callback_data=f"surah_{num}"
        )
    builder.adjust(1)

    total = (len(sura_nums) + PAGES_PER_PAGE - 1) // PAGES_PER_PAGE
    nav = []
    if page > 1:
        nav.append(("⬅️ Oldingi", f"surah_page_{page-1}"))
    if page < total:
        nav.append(("Keyingi ➡️", f"surah_page_{page+1}"))
    for t, c in nav:
        builder.button(text=t, callback_data=c)
    if nav:
        builder.adjust(1, len(nav))
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

def get_after_keyboard():
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
        "Sura tanlang 👇",
        reply_markup=get_sura_list_keyboard(1)
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^surah_page_(\d+)$"))
async def surah_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\n"
        "Sura tanlang 👇",
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

    await callback.answer("Yuklanmoqda... ⏳")

    # 1. Chiroyli karta rasm
    try:
        card_bytes = create_quran_card(sura_num, sura)
        photo = BufferedInputFile(card_bytes, filename=f"sura_{sura_num}.jpg")
        await callback.message.answer_photo(
            photo=photo,
            caption=(
                f"🎵 <b>{sura_num}. {sura['name']} — {sura['arabic']}</b>\n"
                f"({sura['ayat']} oyat) | Qori: Mishary Rashid al-Afasy"
            )
        )
    except Exception:
        # Fallback — matn bilan
        await callback.message.answer(
            f"<b>{sura_num}. {sura['name']} ({sura['arabic']})</b>\n\n"
            f"<pre>{sura['ar']}</pre>\n"
            f"<i>{sura['lat']}</i>\n\n"
            f"📖 {sura['tafsir']}"
        )

    # 2. Audio
    try:
        audio = URLInputFile(
            get_audio_url(sura_num),
            filename=f"{sura['name']}.mp3"
        )
        await callback.message.answer_audio(
            audio=audio,
            title=f"{sura_num}. {sura['name']} — {sura['arabic']}",
            performer="Mishary Rashid al-Afasy",
            reply_markup=get_after_keyboard()
        )
    except Exception:
        await callback.message.answer(
            f"🔗 Audio: {get_audio_url(sura_num)}",
            reply_markup=get_after_keyboard()
        )
