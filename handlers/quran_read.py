"""
📗 Qur'on tajvidli o'qish bo'limi
- Arabcha tajvidli matn (katta shrift)
- Lotincha o'qilishi
- Shayx Muhammad Sodiqning sharhi
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# ============================================================
# SURALAR MA'LUMOTLARI (arabcha + lotin + sharh)
# ============================================================
SURAS_READ = {
    1: {
        "name": "Al-Fotiha",
        "arabic_name": "الفاتحة",
        "ayat_count": 7,
        "ayats": [
            {
                "num": 1,
                "arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                "latin": "Bismillāhir-raḥmānir-raḥīm",
                "tajwid_notes": "بِسْمِ — ba harfi kasra bilan | اللَّهِ — lam shamsiya | الرَّحْمَٰنِ — ra tashdid, madd",
                "sharh": "«Allohning ismi bilan boshlayman, U Rahman (dunyoda barcha mahluqotga rahm qiluvchi) va Rahim (oxiratda faqat mo'minlarga rahm qiluvchi)dir.» Shayx Muhammad Sodiq: Bu oyat bilan har bir yaxshi ishni boshlash Sunnatdir. Allohning ism-sifatlari ichida ar-Rahman — uning kengligi, ar-Rahim — uning chuqurligi va doimiyligini bildiradi."
            },
            {
                "num": 2,
                "arabic": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
                "latin": "Alḥamdu lillāhi rabbil-'ālamīn",
                "tajwid_notes": "الْحَمْدُ — alif lam qamariya | رَبِّ — ra tashdid | الْعَالَمِينَ — madd tabi'iy (2 harakat)",
                "sharh": "«Barcha hamdu sanolar Alloh uchundir, U olamlar Rabbidir.» Shayx Muhammad Sodiq: 'Hamd' — faqat tildan emas, yurak va amaldan chiqadigan maqtov. 'Rabb' — yaratuvchi, tarbiyalovchi, barcha narsani boshqaruvchi degani. 'Olamlar' — ins, jin, farishta, hayvon, o'simlik — hammasi Allohning mulki."
            },
            {
                "num": 3,
                "arabic": "الرَّحْمَٰنِ الرَّحِيمِ",
                "latin": "Ar-raḥmānir-raḥīm",
                "tajwid_notes": "الرَّحْمَٰنِ — lam shamsiya (r harfiga idgom) | madd tabi'iy",
                "sharh": "«Rahman va Rahim.» Shayx Muhammad Sodiq: Bu ism-sifatlar ikkinchi marta takrorlanishi — Allohning rahmati cheksiz ekanligiga urgʻu berish uchun. Rahman — kengligi, Rahim — doimiyligini bildiradi. Fotiha surasida Alloh avval Rabb (Ega), keyin Rahman va Rahim (Rahmdil) sifati bilan tanishtiriladi."
            },
            {
                "num": 4,
                "arabic": "مَالِكِ يَوْمِ الدِّينِ",
                "latin": "Māliki yawmid-dīn",
                "tajwid_notes": "مَالِكِ — madd tabi'iy | يَوْمِ — yaw harflari | الدِّينِ — lam shamsiya, dal tashdid",
                "sharh": "«Qiyomat kunining Egasi.» Shayx Muhammad Sodiq: Dunyo hayotida insonga ko'plab egaliklar berilgan — uy, mol, mansab. Ammo Qiyomat kuni hamma narsa Allohga qaytadi. Bu oyat insonni dunyoga aldanmaslikka undaydi. 'Din' so'zi bu yerda hisob-kitob, mukofot va jazo kuni ma'nosida."
            },
            {
                "num": 5,
                "arabic": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
                "latin": "Iyyāka na'budu wa-iyyāka nasta'īn",
                "tajwid_notes": "إِيَّاكَ — iya tashdid | نَعْبُدُ — waqf mumkin | نَسْتَعِينُ — madd tabi'iy oxirda",
                "sharh": "«Faqat Senga ibodat qilamiz va faqat Sendan yordam so'raymiz.» Shayx Muhammad Sodiq: Bu oyat — Islomning mohiyati. «Iyyaka» (faqat Seni) — shirkdan xalos bo'lish. Ibodat va istianat (yordam so'rash) — ikkisi ham Allohga xos. Ko'plik (biz) ishlatilishi — jamoa bo'lib ibodat qilishning fazilati."
            },
            {
                "num": 6,
                "arabic": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
                "latin": "Ihdinaṣ-ṣirāṭal-mustaqīm",
                "tajwid_notes": "اهْدِنَا — sukun | الصِّرَاطَ — lam shamsiya, sad tashdid | الْمُسْتَقِيمَ — madd tabi'iy",
                "sharh": "«Bizni to'g'ri yo'lga hidoyat qil.» Shayx Muhammad Sodiq: Inson kuniga 17 marta (farz namozlarida) shu duoni o'qiydi — bu hidoyatning qanchalik muhimligini ko'rsatadi. To'g'ri yo'l — Alloh va uning Rasuli ko'rsatgan yo'l. Hidoyat — faqat Allohdan."
            },
            {
                "num": 7,
                "arabic": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
                "latin": "Ṣirāṭal-ladhīna an'amta 'alayhim, ghayril-maghḍūbi 'alayhim wa-laḍ-ḍāllīn",
                "tajwid_notes": "أَنْعَمْتَ — nun iqfa (mim oldida) | الْمَغْضُوبِ — ghain | الضَّالِّينَ — zod tashdid, madd lazim (6 harakat)",
                "sharh": "«Ularga ne'mat berganlaringning yo'li — g'azabga uchraganlar va adashganlar yo'li emas.» Shayx Muhammad Sodiq: Ne'mat berilganlar — payg'ambarlar, siddiqlar, shahidlar va solihlar. G'azabga uchraganlar — haqni bilib rad etganlar. Adashganlar — bilmay yo'ldan chiqqanlar. Har namozda bu duoni o'qib, Allohdan yordam so'raymiz."
            }
        ]
    },
    112: {
        "name": "Al-Ixlos",
        "arabic_name": "الإخلاص",
        "ayat_count": 4,
        "ayats": [
            {
                "num": 1,
                "arabic": "قُلْ هُوَ اللَّهُ أَحَدٌ",
                "latin": "Qul huwallāhu aḥad",
                "tajwid_notes": "قُلْ — lom sukun (waqf) | هُوَ — ha-waw | اللَّهُ — lam shamsiya yo'q (lam qamariya) | أَحَدٌ — tanvin",
                "sharh": "«Ayting: U — Alloh, Yagonadir.» Shayx Muhammad Sodiq: Bu sura Allohning tavsifi. 'Ahad' — mutlaq yagonalik, sherik yo'q. Bu sura Qur'onning uchdan biriga tengdir, chunki Allohning zotini to'liq bayon etadi."
            },
            {
                "num": 2,
                "arabic": "اللَّهُ الصَّمَدُ",
                "latin": "Allāhuṣ-ṣamad",
                "tajwid_notes": "الصَّمَدُ — lam shamsiya, sad tashdid | tanvin oxirda",
                "sharh": "«Alloh — As-Samad (barcha muhtoj, U hech narsaga muhtoj emas).» Shayx Muhammad Sodiq: 'Samad' — hamma unga murojaat qiladi, U hech kimga murojaat qilmaydi. Har qanday ehtiyoj — oziq-ovqat, bilim, kuch — oxir-oqibat Allohdan."
            },
            {
                "num": 3,
                "arabic": "لَمْ يَلِدْ وَلَمْ يُولَدْ",
                "latin": "Lam yalid wa-lam yūlad",
                "tajwid_notes": "لَمْ — mim sukun | يَلِدْ — dal sukun | وَلَمْ — waw atf | يُولَدْ — waw madd",
                "sharh": "«U tug'ilmagan va tug'ilmagan.» Shayx Muhammad Sodiq: Bu oyat xristianlik (Iso — Allohning o'g'li) va boshqa e'tiqodlarni rad etadi. Alloh azaliydir, abadiydir. Tug'ilish — yaratilganlik belgisi. Alloh yaratilmagan."
            },
            {
                "num": 4,
                "arabic": "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
                "latin": "Wa-lam yakul-lahū kufuwan aḥad",
                "tajwid_notes": "وَلَمْ — waw atf | يَكُن — nun sukun (idgom) | لَّهُ — lam tashdid | كُفُوًا — tanvin mansubda | أَحَدٌ — tanvin",
                "sharh": "«Va hech kim Unga teng emas.» Shayx Muhammad Sodiq: Bu sura tawhidning — Allohning yagonaligi e'tiqodining — eng qisqa va to'liq bayoni. Shu sababli uni ko'p o'qish katta savob — har o'qishda Qur'onning uchdan birini o'qigandek bo'ladi."
            }
        ]
    },
    113: {
        "name": "Al-Falaq",
        "arabic_name": "الفلق",
        "ayat_count": 5,
        "ayats": [
            {
                "num": 1,
                "arabic": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
                "latin": "Qul a'ūdhu bi-rabbil-falaq",
                "tajwid_notes": "أَعُوذُ — hamza + madd | بِرَبِّ — ra tashdid | الْفَلَقِ — lam qamariya",
                "sharh": "«Ayting: Tongning Rabbiga panoh topaman.» Shayx Muhammad Sodiq: 'Falaq' — tong yorug'i, bu Allohning qudratining belgisi. Panoh so'rash — zaiflikning emas, aqllilikning belgisi."
            },
            {
                "num": 2,
                "arabic": "مِن شَرِّ مَا خَلَقَ",
                "latin": "Min sharri mā khalaq",
                "tajwid_notes": "مِن شَرِّ — nun iqfa | شَرِّ — ra tashdid | مَا خَلَقَ — madd tabi'iy",
                "sharh": "«U yaratgan narsalarning yovuzligidan.» Shayx Muhammad Sodiq: Bu keng umumiy panoh — barcha yomonliklardan, jumladan kasallik, jaholat, zulm, falokat."
            },
            {
                "num": 3,
                "arabic": "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ",
                "latin": "Wa-min sharri ghāsiqin idhā waqab",
                "tajwid_notes": "وَمِن — mim iqfa | شَرِّ — ra tashdid | غَاسِقٍ — tanvin | إِذَا — alif madd",
                "sharh": "«Qorong'i kechaning yovuzligidan.» Shayx Muhammad Sodiq: Kecha — jinlar va shaytonlar faollashadi, yirtqichlar chiqadi, xavf kuchayadi. Uxlashdan oldin muavvizatayn (Falaq va Nas) o'qish Sunnat."
            },
            {
                "num": 4,
                "arabic": "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ",
                "latin": "Wa-min sharrin-naffāthāti fil-'uqad",
                "tajwid_notes": "النَّفَّاثَاتِ — lam shamsiya, fa tashdid | فِي — madd tabi'iy | الْعُقَدِ — lam qamariya",
                "sharh": "«Tugunlarga puflaydiganlarning yovuzligidan.» Shayx Muhammad Sodiq: Sehrgarlar, ko'z tegadigan odamlar. Islomda sehr haqiqat, lekin Allohga tesha urmaydi. Muavvizatayn — sihrdan eng kuchli himoya."
            },
            {
                "num": 5,
                "arabic": "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ",
                "latin": "Wa-min sharri ḥāsidin idhā ḥasad",
                "tajwid_notes": "وَمِن — iqfa | حَاسِدٍ — tanvin | إِذَا — alif madd | حَسَدَ — waqf joiz",
                "sharh": "«Hasad qilgan hasadchining yovuzligidan.» Shayx Muhammad Sodiq: Hasad — boshqa birovdagi ne'matning yo'qolishini xohlash. Bu eng xavfli kasallik — nafaqat boshqaga, balki o'ziga ham zarar. Allohdan panoh so'rash — bu kasallikdan eng yaxshi davo."
            }
        ]
    },
    114: {
        "name": "An-Nas",
        "arabic_name": "الناس",
        "ayat_count": 6,
        "ayats": [
            {
                "num": 1,
                "arabic": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
                "latin": "Qul a'ūdhu bi-rabbin-nās",
                "tajwid_notes": "أَعُوذُ — madd | بِرَبِّ — ra tashdid | النَّاسِ — lam shamsiya, nun tashdid",
                "sharh": "«Ayting: Odamlarning Rabbiga panoh topaman.» Shayx Muhammad Sodiq: Bu surada Alloh uch sifat bilan — Rabb, Malik, Ilohi — tanishtiriladi. Uchta sifat — uchta munosabat: yaratish, boshqarish, ibodat."
            },
            {
                "num": 2,
                "arabic": "مَلِكِ النَّاسِ",
                "latin": "Malikin-nās",
                "tajwid_notes": "مَلِكِ — kasra kasra | النَّاسِ — shamsiya",
                "sharh": "«Odamlarning Podshohi.» Shayx Muhammad Sodiq: Dunyo podshohlari o'tkinchi. Haqiqiy Podshoh — Alloh. U hech narsaga muhtoj bo'lmagan Hukmdor."
            },
            {
                "num": 3,
                "arabic": "إِلَٰهِ النَّاسِ",
                "latin": "Ilāhin-nās",
                "tajwid_notes": "إِلَٰهِ — alif madd | النَّاسِ — shamsiya",
                "sharh": "«Odamlarning Ilohiga.» Shayx Muhammad Sodiq: Ilohi — ibodatga loyiq. Faqat Alloh ibodatga loyiq. Shu uchta sifatda — Rabb, Malik, Ilohi — Allohning to'liq haqqi bayon etiladi."
            },
            {
                "num": 4,
                "arabic": "مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ",
                "latin": "Min sharril-waswāsil-khannās",
                "tajwid_notes": "مِن شَرِّ — iqfa | الْوَسْوَاسِ — lam qamariya, madd | الْخَنَّاسِ — xun tashdid, madd",
                "sharh": "«Vasvas qiluvchi, qaytib ketuvchi (shayton) ning yovuzligidan.» Shayx Muhammad Sodiq: Shayton doimiy vasvas soladi. Alloh esga olinsa — qochadi ('xannos'). Zikr — shayton qochishining eng kuchli quroli."
            },
            {
                "num": 5,
                "arabic": "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ",
                "latin": "Al-ladhī yuwaswisu fī ṣudūrin-nās",
                "tajwid_notes": "الَّذِي — lam shamsiya | يُوَسْوِسُ — waw madd | فِي — madd | صُدُورِ — madd tabi'iy",
                "sharh": "«U odamlarning ko'ngillariga vasvas soladi.» Shayx Muhammad Sodiq: Shayton ko'ngilga kirib, yomon fikrlarni ilhom beradi. Yaxshi fikrlar — malaklardan, yomon fikrlar — shaytondadn. Farqi — yaxshi fikr yaxshilikka, yomon fikr yomonlikka undaydi."
            },
            {
                "num": 6,
                "arabic": "مِنَ الْجِنَّةِ وَالنَّاسِ",
                "latin": "Minal-jinnati wan-nās",
                "tajwid_notes": "مِنَ — fatha | الْجِنَّةِ — jim tashdid | وَالنَّاسِ — shamsiya, waqf",
                "sharh": "«Jinlardan ham, odamlardan ham.» Shayx Muhammad Sodiq: Vasvas faqat jindan emas — yomon odamlar ham vasvas beradi. Shuning uchun yomon do'stlardan, yomon muhitdan saqlaning. Bu sura bilan Qur'on tugaydi — oxiridagi vasvasdan himoya bilan."
            }
        ]
    }
}

# ============================================================
# SURALAR RO'YXATI
# ============================================================
def get_quran_read_menu():
    builder = InlineKeyboardBuilder()
    for num, sura in SURAS_READ.items():
        builder.button(
            text=f"📗 {num}. {sura['name']} ({sura['arabic_name']})",
            callback_data=f"read_sura_{num}"
        )
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

def get_ayat_keyboard(sura_num: int, ayat_num: int, total: int):
    builder = InlineKeyboardBuilder()
    row = []
    if ayat_num > 1:
        row.append(("⬅️ Oldingi", f"read_ayat_{sura_num}_{ayat_num-1}"))
    if ayat_num < total:
        row.append(("Keyingi ➡️", f"read_ayat_{sura_num}_{ayat_num+1}"))
    for text, cb in row:
        builder.button(text=text, callback_data=cb)
    if row:
        builder.adjust(len(row))
    builder.button(text="📋 Sura ro'yxati", callback_data="menu_quran_read")
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(*([len(row)] if row else []), 2)
    return builder.as_markup()

# ============================================================
# HANDLERS
# ============================================================
@router.callback_query(F.data == "menu_quran_read")
async def quran_read_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📗 <b>Qur'on tajvidli o'qish bo'limi</b>\n\n"
        "Har bir oyat uchun:\n"
        "• <b>Arabcha matn</b> — katta shrift\n"
        "• <b>Lotincha o'qilishi</b> — talaffuz uchun\n"
        "• <b>Tajvid izohi</b> — qoidalar\n"
        "• <b>Shayx Muhammad Sodiq sharhi</b>\n\n"
        "Qaysi surani o'qiysiz?",
        reply_markup=get_quran_read_menu()
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^read_sura_(\d+)$"))
async def read_sura(callback: CallbackQuery):
    sura_num = int(callback.data.split("_")[2])
    sura = SURAS_READ.get(sura_num)
    if not sura:
        await callback.answer("Sura topilmadi!")
        return
    await callback.message.edit_text(
        f"📗 <b>{sura_num}. {sura['name']} — {sura['arabic_name']}</b>\n"
        f"({sura['ayat_count']} oyat)\n\n"
        f"1-oyatdan boshlaymizmi?",
        reply_markup=get_ayat_keyboard(sura_num, 1, sura['ayat_count'])
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^read_ayat_(\d+)_(\d+)$"))
async def read_ayat(callback: CallbackQuery):
    parts = callback.data.split("_")
    sura_num = int(parts[2])
    ayat_num = int(parts[3])
    sura = SURAS_READ.get(sura_num)
    if not sura:
        await callback.answer("Sura topilmadi!")
        return
    ayat = sura["ayats"][ayat_num - 1]

    text = (
        f"📗 <b>{sura_num}. {sura['name']}</b> | {ayat_num}/{sura['ayat_count']}-oyat\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>🕌 Arabcha (tajvidli):</b>\n"
        f"<pre>{ayat['arabic']}</pre>\n\n"
        f"<b>🔤 Lotincha o'qilishi:</b>\n"
        f"<i>{ayat['latin']}</i>\n\n"
        f"<b>📌 Tajvid qoidalari:</b>\n"
        f"{ayat['tajwid_notes']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📚 Shayx Muhammad Sodiq sharhi:</b>\n"
        f"{ayat['sharh']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_ayat_keyboard(sura_num, ayat_num, sura['ayat_count'])
    )
    await callback.answer()
