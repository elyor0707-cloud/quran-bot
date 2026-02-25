"""
🎵 Qur'on audiolari — Chiroyli karta uslubida
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image, ImageDraw, ImageFont
import io, textwrap

router = Router()

SURAS = {
    1: {"name":"Al-Fotiha","arabic":"الفاتحة","ayat":7,
        "ar":"بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
        "lat":"Bismillahir-rahmanir-rahim",
        "tafsir":"Fotiha — «Ochuvchi» demak. Bu sura Qur'onning kirish qismi bo'lib, namozda 17 marta o'qiladi. Shayx Muhammad Sodiq: «Fotiha — qisqa, lekin Qur'onning mohiyatini o'zida jamlagan. Bu surani chuqur tushungan odam Islomning mohiyatini tushungan. Alloh taolo bu surani banda va o'rtasidagi muloqot sifatida yaratgan.»"},
    2: {"name":"Al-Baqara","arabic":"البقرة","ayat":286,
        "ar":"الٓمٓ",
        "lat":"Alif-Laam-Miim",
        "tafsir":"Al-Baqara — «Sigir» surasi. Qur'onning eng uzun surasi (286 oyat). Shayx Muhammad Sodiq: «Uyingizda muntazam o'qilsa, shayton kirmaydi. Unda islom hayotining barcha sohalari — ibodat, muomala, oila, huquq — batafsil bayon etilgan.»"},
    3: {"name":"Ali Imron","arabic":"آل عمران","ayat":200,
        "ar":"الٓمٓ",
        "lat":"Alif-Laam-Miim",
        "tafsir":"Ali Imron — Imron oilasi. 200 oyat. Shayx Muhammad Sodiq: «Bu sura xristianlar bilan munosabat, Iso alayhissalom haqiqati va mo'minlar xususiyatlarini bayon etadi. Jumuada Al-Kahf bilan birga o'qish tavsiya etiladi.»"},
    4: {"name":"An-Niso","arabic":"النساء","ayat":176,
        "ar":"يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ",
        "lat":"Ya ayyuhan-nasut-taqu rabbakum",
        "tafsir":"An-Niso — Ayollar surasi. 176 oyat. Shayx Muhammad Sodiq: «Bu surada meros, nikoh, ayollar huquqlari, urush va sulh haqida batafsil ko'rsatmalar berilgan. Islom huquqining asosi.»"},
    5: {"name":"Al-Moida","arabic":"المائدة","ayat":120,
        "ar":"يَا أَيُّهَا الَّذِينَ آمَنُوا أَوْفُوا بِالْعُقُودِ",
        "lat":"Ya ayyuhal-ladhina amanu awfu bil-uqud",
        "tafsir":"Al-Moida — Dasturxon. 120 oyat. Shayx Muhammad Sodiq: «Qur'onning so'nggi nozil bo'lgan suralari. Halol-harom ovqatlar, ahd-pakt va adolat qoidalari bayon etilgan.»"},
    36: {"name":"Yosin","arabic":"يس","ayat":83,
         "ar":"يسٓ",
         "lat":"Yaa-Siin",
         "tafsir":"Yosin — Qur'on qalbi. 83 oyat. Shayx Muhammad Sodiq: «Bu surani har kuni o'qish katta savob. O'liklar huzurida o'qiladi — chunki Qiyomat, tirilish va oxirat haqida. Mishary Rashid ovozida eshitish yurakni yumshatadi.»"},
    55: {"name":"Ar-Rohman","arabic":"الرحمن","ayat":78,
         "ar":"الرَّحْمَنُ",
         "lat":"Ar-Rahman",
         "tafsir":"Ar-Rohman — Rahman (Mehribon). 78 oyat. Shayx Muhammad Sodiq: «Bu surada 31 marta «Rabbingizning qaysi ne'matini inkor etasiz?» oyati takrorlanadi — har marta yangi ne'mat eslatiladi. Bu sura shukr darsligidir.»"},
    56: {"name":"Al-Voqe'a","arabic":"الواقعة","ayat":96,
         "ar":"إِذَا وَقَعَتِ الْوَاقِعَةُ",
         "lat":"Idha waqa'atil-waqi'ah",
         "tafsir":"Al-Voqe'a — Voqea (Qiyomat). 96 oyat. Shayx Muhammad Sodiq: «Har kecha o'qilsa — faqirlikdan himoya. Bu surada odamlar uch guruhga bo'linishi batafsil bayon etilgan.»"},
    67: {"name":"Al-Mulk","arabic":"الملك","ayat":30,
         "ar":"تَبَارَكَ الَّذِي بِيَدِهِ الْمُلْكُ",
         "lat":"Tabarakal-ladhi biyadihil-mulk",
         "tafsir":"Al-Mulk — Saltanat. 30 oyat. Shayx Muhammad Sodiq: «Bu surani har kecha uxlashdan oldin o'qing — qabr azobidan himoya. Payg'ambar (s.a.v.) uni hech qachon tark etmaganlar.»"},
    78: {"name":"An-Naba","arabic":"النبأ","ayat":40,
         "ar":"عَمَّ يَتَسَاءَلُونَ",
         "lat":"'Amma yatasa'alun",
         "tafsir":"An-Naba — Ulug' xabar. 40 oyat. Shayx Muhammad Sodiq: «Bu sura Qiyomat kuni va uning belgilari haqida. Kichik suralarga kiradi, ammo savob katta.»"},
    108: {"name":"Al-Kavsar","arabic":"الكوثر","ayat":3,
          "ar":"إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
          "lat":"Inna a'taynaka-l-kawsar",
          "tafsir":"Al-Kavsar — Ko'payish. 3 oyat — Qur'onning eng qisqa surasi. Shayx Muhammad Sodiq: «Kavsar — jannatdagi havuz va Payg'ambarga berilgan barcha ne'mat. Bu sura dushmanlarni xo'rlashni bashorat qilgan.»"},
    112: {"name":"Al-Ixlos","arabic":"الإخلاص","ayat":4,
          "ar":"قُلْ هُوَ اللَّهُ أَحَدٌ",
          "lat":"Qul huwallahu ahad",
          "tafsir":"Al-Ixlos — Xolislik. 4 oyat. Shayx Muhammad Sodiq: «Bu sura Qur'onning uchdan biriga teng — chunki Allohning zotini to'liq bayon etadi. Har kuni 3 marta o'qish — Qur'onni bir marta o'qigandek.»"},
    113: {"name":"Al-Falaq","arabic":"الفلق","ayat":5,
          "ar":"قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
          "lat":"Qul a'udhu bi-rabbil-falaq",
          "tafsir":"Al-Falaq — Tong. 5 oyat. Shayx Muhammad Sodiq: «Bu sura — panoh surasi. Uxlashdan oldin o'qing. Mehr, sehr, hasad va kecha yovuzliklaridan himoya. Falaq + Nas birga o'qilsa — to'liq himoya.»"},
    114: {"name":"An-Nas","arabic":"الناس","ayat":6,
          "ar":"قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
          "lat":"Qul a'udhu bi-rabbin-nas",
          "tafsir":"An-Nas — Odamlar. 6 oyat — Qur'onning oxirgi surasi. Shayx Muhammad Sodiq: «Allohga uch sifat — Rabb, Malik, Ilohi — bilan murojaat etiladi. Har kecha uxlashdan oldin o'qing — shayton vasvasidan himoya.»"},
}

PAGES_PER_PAGE = 8
SERIF  = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def _font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def create_quran_card(sura_num: int, sura: dict) -> bytes:
    W = 900
    GOLD  = (255, 212, 75)
    WHITE = (255, 255, 255)
    LIGHT = (218, 234, 220)
    LINE  = (75, 142, 102)
    PAD   = 60   # gorizontal chegara

    # Fontlar
    fh  = _font(SANS_B, 22)
    fla = _font(SANS_B, 24)
    flb = _font(SANS_B, 20)
    ftx = _font(SANS,   18)
    fft = _font(SANS_B, 20)

    # — Arabcha autofit —
    ar_text = sura["ar"]
    ar_size = 110
    probe = Image.new("RGB", (W, 10))
    probe_d = ImageDraw.Draw(probe)
    while ar_size > 28:
        far = _font(SERIF, ar_size)
        b = probe_d.textbbox((0,0), ar_text, font=far)
        if b[2]-b[0] <= W - PAD*2:
            break
        ar_size -= 4

    # — Balandlikni hisoblash —
    b = probe_d.textbbox((0,0), ar_text, font=far)
    ar_h = b[3]-b[1]
    b = probe_d.textbbox((0,0), sura["lat"], font=fla)
    lat_h = b[3]-b[1]
    wrapped_tafsir = textwrap.wrap(sura["tafsir"], width=62)
    tafsir_block_h = 32 + len(wrapped_tafsir)*26

    # Balandlik: yuqori bo'limlar + tafsir + pastki bo'lim
    H = (20 + 36 +       # sarlavha + chiziq
         12 + ar_h +     # arabcha
         10 + lat_h +    # lotincha
         22 +            # chiziq
         tafsir_block_h+ # tafsir
         30 +            # bo'sh joy
         60)             # pastki (chiziq + matn + chiziq)
    H = max(580, H)

    # — Rasm yaratish —
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Gradient
    for y in range(H):
        ratio = y / H
        r = int(15 + ratio * 18)
        g = int(62 + ratio * 35)
        b_c = int(42 + ratio * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b_c))

    # Bezak doiralar
    draw.ellipse([(-80,-80),(200,200)], fill=(28,88,58))
    draw.ellipse([(W-200,H-200),(W+80,H+80)], fill=(18,72,50))
    draw.ellipse([(W-240,-60),(W-40,140)], fill=(23,80,54))
    draw.ellipse([(20,H-180),(200,H+60)], fill=(16,68,46))

    def cx(text, font):
        try:
            b = draw.textbbox((0,0), text, font=font)
            return max(PAD, (W-(b[2]-b[0]))//2)
        except: return PAD

    # Sarlavha
    y = 20
    header = "Qur'oniy oyat"
    draw.text((cx(header,fh), y), header, font=fh, fill=GOLD)
    y += 36
    draw.line([(PAD,y),(W-PAD,y)], fill=GOLD, width=1)
    y += 12

    # Arabcha
    draw.text((cx(ar_text,far), y), ar_text, font=far, fill=WHITE)
    y += ar_h + 10

    # Lotincha
    draw.text((cx(sura["lat"],fla), y), sura["lat"], font=fla, fill=GOLD)
    y += lat_h + 18

    # Chiziq
    draw.line([(PAD,y),(W-PAD,y)], fill=LINE, width=1)
    y += 16

    # Tafsir
    draw.text((PAD, y), "Tafsir:", font=flb, fill=GOLD)
    y += 32
    for line in wrapped_tafsir:
        draw.text((PAD, y), line, font=ftx, fill=LIGHT)
        y += 26

    # Pastki chiziq va sarlavha
    y_bot = H - 55
    draw.line([(PAD,y_bot),(W-PAD,y_bot)], fill=LINE, width=1)
    footer = f"{sura['name']} surasi  |  1-oyat"
    draw.text((cx(footer,fft), y_bot+10), footer, font=fft, fill=GOLD)
    draw.line([(PAD,H-16),(W-PAD,H-16)], fill=GOLD, width=1)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.read()

def get_audio_url(sura_num): 
    return f"https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/{sura_num:03d}.mp3"

def get_sura_list_keyboard(page=1):
    builder = InlineKeyboardBuilder()
    nums = sorted(SURAS.keys())
    start = (page-1)*PAGES_PER_PAGE
    for num in nums[start:start+PAGES_PER_PAGE]:
        s = SURAS[num]
        builder.button(text=f"🎵 {num}. {s['name']} ({s['arabic']})", callback_data=f"surah_{num}")
    builder.adjust(1)
    total = (len(nums)+PAGES_PER_PAGE-1)//PAGES_PER_PAGE
    nav = []
    if page>1: nav.append(("⬅️ Oldingi",f"surah_page_{page-1}"))
    if page<total: nav.append(("Keyingi ➡️",f"surah_page_{page+1}"))
    for t,c in nav: builder.button(text=t, callback_data=c)
    if nav: builder.adjust(1,len(nav))
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

def get_after_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Suralar ro'yxati", callback_data="menu_quran")
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(F.data == "menu_quran")
async def quran_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\nSura tanlang 👇",
        reply_markup=get_sura_list_keyboard(1)
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^surah_page_(\d+)$"))
async def surah_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\nSura tanlang 👇",
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
    try:
        card_bytes = create_quran_card(sura_num, sura)
        photo = BufferedInputFile(card_bytes, filename=f"sura_{sura_num}.jpg")
        await callback.message.answer_photo(
            photo=photo,
            caption=f"🎵 <b>{sura_num}. {sura['name']} — {sura['arabic']}</b>\n({sura['ayat']} oyat) | Qori: Mishary Rashid al-Afasy"
        )
    except Exception:
        await callback.message.answer(
            f"<b>{sura_num}. {sura['name']}</b>\n<pre>{sura['ar']}</pre>\n<i>{sura['lat']}</i>\n\n📖 {sura['tafsir']}"
        )
    try:
        audio = URLInputFile(get_audio_url(sura_num), filename=f"{sura['name']}.mp3")
        await callback.message.answer_audio(
            audio=audio,
            title=f"{sura_num}. {sura['name']} — {sura['arabic']}",
            performer="Mishary Rashid al-Afasy",
            reply_markup=get_after_keyboard()
        )
    except Exception:
        await callback.message.answer(f"🔗 Audio: {get_audio_url(sura_num)}", reply_markup=get_after_keyboard())
