"""
🎵 Qur'on audiolari — 2-rasmdagi uslubda
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image, ImageDraw, ImageFont
import io, textwrap

router = Router()

SURAS = {
    1:   {"name":"Al-Fotiha",    "arabic":"الفاتحة",    "ayat":7,
          "ar":"بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
          "lat":"Bismillahir-rahmanir-rahim",
          "tafsir":"Fotiha — «Ochuvchi» demak. Bu sura Qur'onning kirish qismi bo'lib, namozda 17 marta o'qiladi. Shayx Muhammad Sodiq: «Fotiha — qisqa, lekin Qur'onning mohiyatini o'zida jamlagan. Bu surani chuqur tushungan odam Islomning mohiyatini tushungan.»"},
    2:   {"name":"Al-Baqara",    "arabic":"البقرة",      "ayat":286,
          "ar":"الٓمٓ",
          "lat":"Alif-Laam-Miim",
          "tafsir":"Al-Baqara — «Sigir» surasi. Qur'onning eng uzun surasi (286 oyat). Shayx Muhammad Sodiq: «Uyingizda muntazam o'qilsa, shayton kirmaydi. Unda islom hayotining barcha sohalari — ibodat, muomala, oila, huquq — batafsil bayon etilgan.»"},
    3:   {"name":"Ali Imron",    "arabic":"آل عمران",   "ayat":200,
          "ar":"الٓمٓ",
          "lat":"Alif-Laam-Miim",
          "tafsir":"Ali Imron — Imron oilasi. 200 oyat. Shayx Muhammad Sodiq: «Bu sura xristianlar bilan munosabat, Iso alayhissalom haqiqati va mo'minlar xususiyatlarini bayon etadi.»"},
    4:   {"name":"An-Niso",      "arabic":"النساء",      "ayat":176,
          "ar":"يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ",
          "lat":"Ya ayyuhan-nasut-taqu rabbakum",
          "tafsir":"An-Niso — Ayollar surasi. 176 oyat. Shayx Muhammad Sodiq: «Bu surada meros, nikoh, ayollar huquqlari, urush va sulh haqida batafsil ko'rsatmalar berilgan.»"},
    5:   {"name":"Al-Moida",     "arabic":"المائدة",     "ayat":120,
          "ar":"يَا أَيُّهَا الَّذِينَ آمَنُوا أَوْفُوا بِالْعُقُودِ",
          "lat":"Ya ayyuhal-ladhina amanu awfu bil-uqud",
          "tafsir":"Al-Moida — Dasturxon. 120 oyat. Shayx Muhammad Sodiq: «Qur'onning so'nggi nozil bo'lgan suralari. Halol-harom ovqatlar, ahd-pakt va adolat qoidalari bayon etilgan.»"},
    6:   {"name":"Al-An'om",     "arabic":"الأنعام",     "ayat":165,
          "ar":"الْحَمْدُ لِلَّهِ الَّذِي خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ",
          "lat":"Alhamdu lillahil-ladhi khalaqas-samawati wal-ard",
          "tafsir":"Al-An'om — Chorva. 165 oyat. Shayx Muhammad Sodiq: «Bu sura Makkada bir kechada nozil bo'lgan. Tavhid, nubuvvat va oxirat — Islomning uch asosi batafsil bayon etilgan.»"},
    7:   {"name":"Al-A'rof",     "arabic":"الأعراف",     "ayat":206,
          "ar":"الٓمٓصٓ",
          "lat":"Alif-Laam-Miim-Saad",
          "tafsir":"Al-A'rof — Balandliklar. 206 oyat. Shayx Muhammad Sodiq: «Bu surada payg'ambarlar tarixi, Muso alayhissalom qissasi va jannat-do'zax o'rtasidagi A'rof haqida so'z boradi.»"},
    8:   {"name":"Al-Anfol",     "arabic":"الأنفال",     "ayat":75,
          "ar":"يَسْأَلُونَكَ عَنِ الْأَنفَالِ",
          "lat":"Yas'alunaka anil-anfal",
          "tafsir":"Al-Anfol — O'ljalar. 75 oyat. Shayx Muhammad Sodiq: «Badr jangidan keyin nozil bo'lgan. Urush qoidalari, o'lja taqsimoti va mo'minlarning sifatlari bayon etilgan.»"},
    9:   {"name":"At-Tavba",     "arabic":"التوبة",      "ayat":129,
          "ar":"بَرَاءَةٌ مِّنَ اللَّهِ وَرَسُولِهِ",
          "lat":"Bara'atun minallahi wa rasulihi",
          "tafsir":"At-Tavba — Tavba. 129 oyat. Shayx Muhammad Sodiq: «Qur'onda bismillahsiz boshlangan yagona sura. Munofiqlar va ularning xususiyatlari haqida juda ko'p ma'lumot beradi.»"},
    10:  {"name":"Yunus",        "arabic":"يونس",        "ayat":109,
          "ar":"الٓرٰ تِلْكَ آيَاتُ الْكِتَابِ الْحَكِيمِ",
          "lat":"Alif-Laam-Ra, tilka ayatul-kitabil-hakim",
          "tafsir":"Yunus — Yunus alayhissalom. 109 oyat. Shayx Muhammad Sodiq: «Bu surada iymon va kufr, dunyo hayotining qisqaligi va Yunus alayhissalom qissasi batafsil bayon etilgan.»"},
    11:  {"name":"Hud",          "arabic":"هود",         "ayat":123,
          "ar":"الٓرٰ كِتَابٌ أُحْكِمَتْ آيَاتُهُ",
          "lat":"Alif-Laam-Ra, kitabun uhkimat ayatuhu",
          "tafsir":"Hud — Hud alayhissalom. 123 oyat. Shayx Muhammad Sodiq: «Bu surani o'qish Payg'ambarimizni qaritatgan — chunki unda qiyomat va unga tayyorlanish haqida juda og'ir oyatlar bor.»"},
    12:  {"name":"Yusuf",        "arabic":"يوسف",        "ayat":111,
          "ar":"الٓرٰ تِلْكَ آيَاتُ الْكِتَابِ الْمُبِينِ",
          "lat":"Alif-Laam-Ra, tilka ayatul-kitabil-mubin",
          "tafsir":"Yusuf — Yusuf alayhissalom. 111 oyat. Shayx Muhammad Sodiq: «Qur'onning eng chiroyli qissasi. Sabr, vafo, kechirish va Allohga tayanish — bu suradagi asosiy darslar.»"},
    13:  {"name":"Ar-Ra'd",      "arabic":"الرعد",       "ayat":43,
          "ar":"الٓمٓرٰ تِلْكَ آيَاتُ الْكِتَابِ",
          "lat":"Alif-Laam-Miim-Ra, tilka ayatul-kitab",
          "tafsir":"Ar-Ra'd — Momaqaldiroq. 43 oyat. Shayx Muhammad Sodiq: «Bu surada momaqaldiroq Allohni tasbih qiladi. Tavhid va Allohning qudrati haqida ajoyib oyatlar mavjud.»"},
    14:  {"name":"Ibrohim",      "arabic":"إبراهيم",     "ayat":52,
          "ar":"الٓرٰ كِتَابٌ أَنزَلْنَاهُ إِلَيْكَ",
          "lat":"Alif-Laam-Ra, kitabun anzalnahu ilayk",
          "tafsir":"Ibrohim — Ibrohim alayhissalom. 52 oyat. Shayx Muhammad Sodiq: «Bu surada Ibrohim alayhissalomning duolari, ayniqsa «Rabbim, bu shaharni xavfsiz qil» duosi bizga namuna.»"},
    15:  {"name":"Al-Hijr",      "arabic":"الحجر",       "ayat":99,
          "ar":"الٓرٰ تِلْكَ آيَاتُ الْكِتَابِ وَقُرْآنٍ مُّبِينٍ",
          "lat":"Alif-Laam-Ra, tilka ayatul-kitabi wa Qur'anim mubin",
          "tafsir":"Al-Hijr — Hijr vodiysi. 99 oyat. Shayx Muhammad Sodiq: «Bu surada Qur'onning muhofazasi va'da qilingan: Alloh uni o'zi saqlaydi. Iblis qissasi va uning mag'rurligidan dars olamiz.»"},
    16:  {"name":"An-Nahl",      "arabic":"النحل",       "ayat":128,
          "ar":"أَتَىٰ أَمْرُ اللَّهِ فَلَا تَسْتَعْجِلُوهُ",
          "lat":"Ata amrullahi fala tasta'jiluhu",
          "tafsir":"An-Nahl — Asalari. 128 oyat. Shayx Muhammad Sodiq: «Asalari surasi — chunki asalari Allohning ilhomi bilan harakat qiladi. Allohning ne'matlari sanab bo'lmaydi — bu suradagi asosiy xabar.»"},
    17:  {"name":"Al-Isro",      "arabic":"الإسراء",     "ayat":111,
          "ar":"سُبْحَانَ الَّذِي أَسْرَىٰ بِعَبْدِهِ لَيْلًا",
          "lat":"Subhanal-ladhi asra bi-abdihi laylan",
          "tafsir":"Al-Isro — Isro. 111 oyat. Shayx Muhammad Sodiq: «Bu surada Meraj kechasi va 17 muhim buyruq — o'g'irlik qilma, zino qilma, ota-onaga yaxshi muomala qil va boshqalar bayon etilgan.»"},
    18:  {"name":"Al-Kahf",      "arabic":"الكهف",       "ayat":110,
          "ar":"الْحَمْدُ لِلَّهِ الَّذِي أَنزَلَ عَلَىٰ عَبْدِهِ الْكِتَابَ",
          "lat":"Alhamdu lillahil-ladhi anzala ala abdhil-kitab",
          "tafsir":"Al-Kahf — G'or. 110 oyat. Shayx Muhammad Sodiq: «Har jumasda o'qiladi — Dajjol fitnasidan himoya. To'rt qissa: g'or yigitlari, bog' egasi, Muso va Xizr, Zulqarnayn.»"},
    19:  {"name":"Maryam",       "arabic":"مريم",        "ayat":98,
          "ar":"كهيعص",
          "lat":"Kaf-Ha-Ya-Ain-Saad",
          "tafsir":"Maryam — Maryam alayhissalom. 98 oyat. Shayx Muhammad Sodiq: «Bu surada Zakariya, Yahyo, Maryam va Iso alayhissalomlar qissasi keltirilgan. Allohning qudratiga iymon mustahkamlanadi.»"},
    20:  {"name":"Toha",         "arabic":"طه",          "ayat":135,
          "ar":"طه",
          "lat":"Taa-Haa",
          "tafsir":"Toha — 20-sura. 135 oyat. Shayx Muhammad Sodiq: «Bu surada Muso alayhissalomning Farone bilan kurashi va oxirida g'alaba qozonishi batafsil bayon etilgan. Sabr va Allohga tayanish darsi.»"},
    21:  {"name":"Al-Anbiyo",    "arabic":"الأنبياء",    "ayat":112,
          "ar":"اقْتَرَبَ لِلنَّاسِ حِسَابُهُمْ",
          "lat":"Iqtaraba lin-nasi hisabuhum",
          "tafsir":"Al-Anbiyo — Payg'ambarlar. 112 oyat. Shayx Muhammad Sodiq: «Bu surada 18 payg'ambar tilga olinadi. Hammasi bir dinni — tavhidni — olib kelgan. Qiyomat yaqinligi eslatiladi.»"},
    22:  {"name":"Al-Hajj",      "arabic":"الحج",        "ayat":78,
          "ar":"يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمْ",
          "lat":"Ya ayyuhan-nasu ittaqu rabbakum",
          "tafsir":"Al-Hajj — Haj. 78 oyat. Shayx Muhammad Sodiq: «Bu surada haj ibodati, qiyomat dahshati va jihod hukmlari bayon etilgan. Sajda oyati mavjud — o'qiganda sajda qilinadi.»"},
    23:  {"name":"Al-Mo'minun",  "arabic":"المؤمنون",    "ayat":118,
          "ar":"قَدْ أَفْلَحَ الْمُؤْمِنُونَ",
          "lat":"Qad aflahal-mu'minun",
          "tafsir":"Al-Mo'minun — Mo'minlar. 118 oyat. Shayx Muhammad Sodiq: «Muvaffaqiyatli mo'minlarning 7 sifati: xushu, zinadan saqlash, amonatga vafo va boshqalar. Bu oyatlar nozil bo'lgach, Payg'ambar xursand bo'ldilar.»"},
    24:  {"name":"An-Nur",       "arabic":"النور",       "ayat":64,
          "ar":"سُورَةٌ أَنزَلْنَاهَا وَفَرَضْنَاهَا",
          "lat":"Suratun anzalnaha wa faradnaha",
          "tafsir":"An-Nur — Nur. 64 oyat. Shayx Muhammad Sodiq: «Bu surada zino jazosi, qazf, Oysha onamizga bo'hton qissasi, hijob hukmi va ijozat so'rash odobi bayon etilgan.»"},
    25:  {"name":"Al-Furqon",    "arabic":"الفرقان",     "ayat":77,
          "ar":"تَبَارَكَ الَّذِي نَزَّلَ الْفُرْقَانَ",
          "lat":"Tabarakal-ladhi nazzalal-furqan",
          "tafsir":"Al-Furqon — Farq qiluvchi. 77 oyat. Shayx Muhammad Sodiq: «Furqon — haq va botilni farq qiluvchi Qur'on. Oxirida Allohning rahmati xizmatkorlarining 10 ta xususiyati bayon etilgan.»"},
    26:  {"name":"Ash-Shuaro",   "arabic":"الشعراء",     "ayat":227,
          "ar":"طسم",
          "lat":"Taa-Siin-Miim",
          "tafsir":"Ash-Shuaro — Shoirlar. 227 oyat. Shayx Muhammad Sodiq: «Bu surada Muso, Ibrohim, Nuh, Hud, Solih va Lut alayhissalomlar qissasi keltirilgan. Shoirlar haqida oxirida alohida bo'lim bor.»"},
    27:  {"name":"An-Naml",      "arabic":"النمل",       "ayat":93,
          "ar":"طس تِلْكَ آيَاتُ الْقُرْآنِ وَكِتَابٍ مُّبِينٍ",
          "lat":"Taa-Siin, tilka ayatul-Qur'ani wa kitabim mubin",
          "tafsir":"An-Naml — Chumoli. 93 oyat. Shayx Muhammad Sodiq: «Sulayman alayhissalom va Bilqis malikasi qissasi, chumoli Sulaymonning lashkarini ogohlantirishi — Alloh barcha jonzotlarga til bergan.»"},
    28:  {"name":"Al-Qasas",     "arabic":"القصص",       "ayat":88,
          "ar":"طسم تِلْكَ آيَاتُ الْكِتَابِ الْمُبِينِ",
          "lat":"Taa-Siin-Miim, tilka ayatul-kitabil-mubin",
          "tafsir":"Al-Qasas — Qissalar. 88 oyat. Shayx Muhammad Sodiq: «Bu surada Muso alayhissalomning tug'ilishidan Faroneni halokatigacha bo'lgan to'liq hayoti bayon etilgan.»"},
    29:  {"name":"Al-Ankabut",   "arabic":"العنكبوت",    "ayat":69,
          "ar":"الٓمٓ أَحَسِبَ النَّاسُ أَن يُتْرَكُوا",
          "lat":"Alif-Laam-Miim, ahasisban-nasu an yuthraku",
          "tafsir":"Al-Ankabut — O'rgimchak. 69 oyat. Shayx Muhammad Sodiq: «O'rgimchak ini eng zaif uy — shuningdek kufr va shirk ham eng zaif poya. Imtihonsiz jannatga kirish mumkin emas.»"},
    30:  {"name":"Ar-Rum",       "arabic":"الروم",       "ayat":60,
          "ar":"الٓمٓ غُلِبَتِ الرُّومُ",
          "lat":"Alif-Laam-Miim, ghulibatir-Rum",
          "tafsir":"Ar-Rum — Rum (Vizantiya). 60 oyat. Shayx Muhammad Sodiq: «Rum g'alaba qozonadi degan bashorat uch-to'qqiz yil ichida isbotlandi — bu Qur'onning mo'jizasi.»"},
    31:  {"name":"Luqmon",       "arabic":"لقمان",       "ayat":34,
          "ar":"الٓمٓ تِلْكَ آيَاتُ الْكِتَابِ الْحَكِيمِ",
          "lat":"Alif-Laam-Miim, tilka ayatul-kitabil-hakim",
          "tafsir":"Luqmon — Luqmon hakim. 34 oyat. Shayx Muhammad Sodiq: «Luqmon o'g'liga bergan 7 ta nasihat — shirk qilma, ota-onaga yaxshi muomala qil, namoz o'qi, yaxshilikka buyur, sabrli bo'l — hammamiz uchun dars.»"},
    32:  {"name":"As-Sajda",     "arabic":"السجدة",      "ayat":30,
          "ar":"الٓمٓ تَنزِيلُ الْكِتَابِ لَا رَيْبَ فِيهِ",
          "lat":"Alif-Laam-Miim, tanzilul-kitabi la rayba fih",
          "tafsir":"As-Sajda — Sajda. 30 oyat. Shayx Muhammad Sodiq: «Payg'ambar Juma kechasi As-Sajda va Al-Insoni o'qirdilar. Sajda oyati mavjud. Jannat va do'zax tasvirining eng ta'sirchan bayoni shu surada.»"},
    33:  {"name":"Al-Ahzob",     "arabic":"الأحزاب",     "ayat":73,
          "ar":"يَا أَيُّهَا النَّبِيُّ اتَّقِ اللَّهَ",
          "lat":"Ya ayyuhan-nabiyyu ittaqillah",
          "tafsir":"Al-Ahzob — Ittifoqchilar. 73 oyat. Shayx Muhammad Sodiq: «Xandaq jangi, hijob hukmi va Payg'ambarga aloqador ko'plab masalalar bayon etilgan. Amonatni ko'tarish haqidagi oyat ham shu surada.»"},
    34:  {"name":"Saba",         "arabic":"سبأ",         "ayat":54,
          "ar":"الْحَمْدُ لِلَّهِ الَّذِي لَهُ مَا فِي السَّمَاوَاتِ",
          "lat":"Alhamdu lillahil-ladhi lahu ma fis-samawat",
          "tafsir":"Saba — Saba malikasi. 54 oyat. Shayx Muhammad Sodiq: «Dovud va Sulayman alayhissalomga berilgan ne'matlar, Saba xalqining shukrsizligi va oqibati haqida ibratli qissa.»"},
    35:  {"name":"Fotir",        "arabic":"فاطر",        "ayat":45,
          "ar":"الْحَمْدُ لِلَّهِ فَاطِرِ السَّمَاوَاتِ وَالْأَرْضِ",
          "lat":"Alhamdu lillahi fatiras-samawati wal-ard",
          "tafsir":"Fotir — Yaratuvchi. 45 oyat. Shayx Muhammad Sodiq: «Alloh yaratishda sherik va yordamchiga muhtoj emas. Farishtallar va ularning vazifalari, Qur'on olimlari — Allohdan eng ko'p qo'rquvchilar.»"},
    36:  {"name":"Yosin",        "arabic":"يس",          "ayat":83,
          "ar":"يسٓ",
          "lat":"Yaa-Siin",
          "tafsir":"Yosin — Qur'on qalbi. 83 oyat. Shayx Muhammad Sodiq: «Bu surani har kuni o'qish katta savob. O'liklar huzurida o'qiladi — chunki Qiyomat, tirilish va oxirat haqida.»"},
    37:  {"name":"As-Soffot",    "arabic":"الصافات",     "ayat":182,
          "ar":"وَالصَّافَّاتِ صَفًّا",
          "lat":"Was-saffati saffa",
          "tafsir":"As-Soffot — Saflangolar. 182 oyat. Shayx Muhammad Sodiq: «Bu surada farishtallar, Ibrohim alayhissalomning o'g'lini qurbon qilish qissasi va mushriklar haqida so'z boradi.»"},
    38:  {"name":"Sod",          "arabic":"ص",           "ayat":88,
          "ar":"صٓ وَالْقُرْآنِ ذِي الذِّكْرِ",
          "lat":"Saad, wal-Qur'ani dhidh-dhikr",
          "tafsir":"Sod — 38-sura. 88 oyat. Shayx Muhammad Sodiq: «Dovud va Sulaymonga berilgan ne'matlar, Ayyub alayhissalomning sabri va Iblisning mag'rurligidan dars olamiz.»"},
    39:  {"name":"Az-Zumar",     "arabic":"الزمر",       "ayat":75,
          "ar":"تَنزِيلُ الْكِتَابِ مِنَ اللَّهِ الْعَزِيزِ الْحَكِيمِ",
          "lat":"Tanzilul-kitabi minallahil-azizil-hakim",
          "tafsir":"Az-Zumar — Guruhlar. 75 oyat. Shayx Muhammad Sodiq: «Qiyomatda odamlar guruh-guruh bo'lib jannat va do'zaxga kiritilishi batafsil tasvirlangan. Tavba eshigi doim ochiq.»"},
    40:  {"name":"Gofir",        "arabic":"غافر",        "ayat":85,
          "ar":"حم تَنزِيلُ الْكِتَابِ مِنَ اللَّهِ",
          "lat":"Haa-Miim, tanzilul-kitabi minallah",
          "tafsir":"Gofir — Kechiruvchi. 85 oyat. Shayx Muhammad Sodiq: «Fir'avn saroyidagi mo'min erkak qissasi — yolg'iz o'zi haqni himoya qildi. Jasorat va iymonning ibratli namunasi.»"},
    41:  {"name":"Fussilat",     "arabic":"فصلت",        "ayat":54,
          "ar":"حم تَنزِيلٌ مِّنَ الرَّحْمَٰنِ الرَّحِيمِ",
          "lat":"Haa-Miim, tanzilum minar-rahmanir-rahim",
          "tafsir":"Fussilat — Batafsil bayon etilgan. 54 oyat. Shayx Muhammad Sodiq: «Bu surada yer va osmoning yaratilishi 6 kunda, Qur'on arabcha nozil etilgani va kofirlarning uzrlari haqida so'z boradi.»"},
    42:  {"name":"Ash-Shura",    "arabic":"الشورى",      "ayat":53,
          "ar":"حم عسق",
          "lat":"Haa-Miim, Ain-Siin-Qaaf",
          "tafsir":"Ash-Shura — Maslahat. 53 oyat. Shayx Muhammad Sodiq: «Islomda shura — jamoa maslahati asosiy tamoyil. Mo'minlar o'z ishlarini o'zaro kengashib hal qiladilar.»"},
    43:  {"name":"Az-Zuxruf",    "arabic":"الزخرف",      "ayat":89,
          "ar":"حم وَالْكِتَابِ الْمُبِينِ",
          "lat":"Haa-Miim, wal-kitabil-mubin",
          "tafsir":"Az-Zuxruf — Tillo bezaklar. 89 oyat. Shayx Muhammad Sodiq: «Dunyo zinati aldamchi — zulqarnayn oltin saroylari ham oxirat oldida hechdir. Iso alayhissalom haqidagi oyatlar ham shu surada.»"},
    44:  {"name":"Ad-Duxon",     "arabic":"الدخان",      "ayat":59,
          "ar":"حم وَالْكِتَابِ الْمُبِينِ إِنَّا أَنزَلْنَاهُ",
          "lat":"Haa-Miim, wal-kitabil-mubin, inna anzalnahu",
          "tafsir":"Ad-Duxon — Tutun. 59 oyat. Shayx Muhammad Sodiq: «Qiyomatdan oldin katta tutun — bu surada eslatilgan. Qadr kechasi ham shu surada tilga olingan.»"},
    45:  {"name":"Al-Josiya",    "arabic":"الجاثية",     "ayat":37,
          "ar":"حم تَنزِيلُ الْكِتَابِ مِنَ اللَّهِ الْعَزِيزِ الْحَكِيمِ",
          "lat":"Haa-Miim, tanzilul-kitabi minallahil-azizil-hakim",
          "tafsir":"Al-Josiya — Tiz cho'kkan. 37 oyat. Shayx Muhammad Sodiq: «Qiyomat kuni barcha ummat tiz cho'kadi. Har kimning kitobi beriladi. Allohning hukmi adolatli va mutlaq.»"},
    46:  {"name":"Al-Ahqof",     "arabic":"الأحقاف",     "ayat":35,
          "ar":"حم تَنزِيلُ الْكِتَابِ مِنَ اللَّهِ الْعَزِيزِ الْحَكِيمِ",
          "lat":"Haa-Miim, tanzilul-kitabi minallahil-azizil-hakim",
          "tafsir":"Al-Ahqof — Qum tepaliklari. 35 oyat. Shayx Muhammad Sodiq: «Od xalqining halokati va jinlarning Qur'on tinglagani qissasi. Ota-onaga yaxshi muomalaning muhimligi ta'kidlangan.»"},
    47:  {"name":"Muhammad",     "arabic":"محمد",        "ayat":38,
          "ar":"الَّذِينَ كَفَرُوا وَصَدُّوا عَن سَبِيلِ اللَّهِ",
          "lat":"Alladhina kafaru wa saddu an sabilillah",
          "tafsir":"Muhammad — Muhammad s.a.v. 38 oyat. Shayx Muhammad Sodiq: «Jihod, mo'minlar va kofirlarning taqdiri, jannat nehrlarining tavsifi shu surada. Alloh mo'minlarni sinab ko'radi.»"},
    48:  {"name":"Al-Fath",      "arabic":"الفتح",       "ayat":29,
          "ar":"إِنَّا فَتَحْنَا لَكَ فَتْحًا مُّبِينًا",
          "lat":"Inna fatahna laka fathan mubina",
          "tafsir":"Al-Fath — G'alaba. 29 oyat. Shayx Muhammad Sodiq: «Hudaybiya sulhi — ko'rinishda mag'lubiyat, aslida katta g'alaba. Allohning rejasi biz bilmagan joydan keladi.»"},
    49:  {"name":"Al-Hujurot",   "arabic":"الحجرات",     "ayat":18,
          "ar":"يَا أَيُّهَا الَّذِينَ آمَنُوا لَا تُقَدِّمُوا",
          "lat":"Ya ayyuhal-ladhina amanu la tuqaddimu",
          "tafsir":"Al-Hujurot — Hujralar. 18 oyat. Shayx Muhammad Sodiq: «Islom axloqining qomusi: Payg'ambarga hurmat, xabarni tekshirish, g'iybat qilmaslik, millat va qabila bilan faxrlanmaslik.»"},
    50:  {"name":"Qof",          "arabic":"ق",           "ayat":45,
          "ar":"قٓ وَالْقُرْآنِ الْمَجِيدِ",
          "lat":"Qaaf, wal-Qur'anil-majid",
          "tafsir":"Qof — 50-sura. 45 oyat. Shayx Muhammad Sodiq: «Payg'ambar Juma va Hayit namozlarida shu surani o'qirdilar. O'lim, qabr va qiyomat haqida qisqa va ta'sirchan bayon.»"},
    51:  {"name":"Az-Zoriyot",   "arabic":"الذاريات",    "ayat":60,
          "ar":"وَالذَّارِيَاتِ ذَرْوًا",
          "lat":"Wadh-dhariyati dharwa",
          "tafsir":"Az-Zoriyot — Sochuvchi shamollar. 60 oyat. Shayx Muhammad Sodiq: «Ibrohim alayhissalom mehmondorchiligining go'zal manzarasi. Allohning qudrati va qiyomat tasvirlari.»"},
    52:  {"name":"At-Tur",       "arabic":"الطور",       "ayat":49,
          "ar":"وَالطُّورِ",
          "lat":"Wat-tur",
          "tafsir":"At-Tur — Tur tog'i. 49 oyat. Shayx Muhammad Sodiq: «Alloh Tur tog'i, yozilgan kitob, Baytul-Ma'mur va to'liq dengiz bilan qasam ichadi. Mo'minlar jannatda oilalari bilan bo'ladilar.»"},
    53:  {"name":"An-Najm",      "arabic":"النجم",       "ayat":62,
          "ar":"وَالنَّجْمِ إِذَا هَوَىٰ",
          "lat":"Wan-najmi idha hawa",
          "tafsir":"An-Najm — Yulduz. 62 oyat. Shayx Muhammad Sodiq: «Meraj kechasi tasvirlangan. Butlarga sig'inish batchida — ularga nom berilgan, xolos. Sajda oyati mavjud.»"},
    54:  {"name":"Al-Qamar",     "arabic":"القمر",       "ayat":55,
          "ar":"اقْتَرَبَتِ السَّاعَةُ وَانشَقَّ الْقَمَرُ",
          "lat":"Iqtarabatis-sa'atu wan-shaqqal-qamar",
          "tafsir":"Al-Qamar — Oy. 55 oyat. Shayx Muhammad Sodiq: «Oy ikki bo'lingani — Payg'ambarning eng katta mo'jizasi. «Qur'on oson qilindi — eslaydiganlar bormi?» oyati 4 marta takrorlanadi.»"},
    55:  {"name":"Ar-Rohman",    "arabic":"الرحمن",      "ayat":78,
          "ar":"الرَّحْمَنُ",
          "lat":"Ar-Rahman",
          "tafsir":"Ar-Rohman — Rahman. 78 oyat. Shayx Muhammad Sodiq: «31 marta «Rabbingizning qaysi ne'matini inkor etasiz?» oyati takrorlanadi. Bu sura shukr darsligidir.»"},
    56:  {"name":"Al-Voqe'a",    "arabic":"الواقعة",     "ayat":96,
          "ar":"إِذَا وَقَعَتِ الْوَاقِعَةُ",
          "lat":"Idha waqa'atil-waqi'ah",
          "tafsir":"Al-Voqe'a — Voqea (Qiyomat). 96 oyat. Shayx Muhammad Sodiq: «Har kecha o'qilsa — faqirlikdan himoya. Bu surada odamlar uch guruhga bo'linishi batafsil bayon etilgan.»"},
    57:  {"name":"Al-Hadid",     "arabic":"الحديد",      "ayat":29,
          "ar":"سَبَّحَ لِلَّهِ مَا فِي السَّمَاوَاتِ وَالْأَرْضِ",
          "lat":"Sabbaha lillahi ma fis-samawati wal-ard",
          "tafsir":"Al-Hadid — Temir. 29 oyat. Shayx Muhammad Sodiq: «Temir Alloh tomonidan yuborilgan ne'mat. Dunyo hayoti — o'yin-kulgi. Haqiqiy hayot — oxirat. Bu sura zohidlarni tarbiyalaydi.»"},
    58:  {"name":"Al-Mujodala",  "arabic":"المجادلة",    "ayat":22,
          "ar":"قَدْ سَمِعَ اللَّهُ قَوْلَ الَّتِي تُجَادِلُكَ",
          "lat":"Qad sami'allahu qawlal-lati tujadiluk",
          "tafsir":"Al-Mujodala — Munozara. 22 oyat. Shayx Muhammad Sodiq: «Xavsala degan ayolning Payg'ambarga shikoyati — Alloh eshitdi va javob berdi. Alloh har bir bandaning dardini eshitadi.»"},
    59:  {"name":"Al-Hashr",     "arabic":"الحشر",       "ayat":24,
          "ar":"سَبَّحَ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
          "lat":"Sabbaha lillahi ma fis-samawati wa ma fil-ard",
          "tafsir":"Al-Hashr — Surgun. 24 oyat. Shayx Muhammad Sodiq: «Suradagi oxirgi uch oyat — Allohning sifatlarini bayon etadigan eng mukammal oyatlar. Har kuni ertalab va kechqurun o'qish tavsiya etiladi.»"},
    60:  {"name":"Al-Mumtahana", "arabic":"الممتحنة",    "ayat":13,
          "ar":"يَا أَيُّهَا الَّذِينَ آمَنُوا لَا تَتَّخِذُوا عَدُوِّي",
          "lat":"Ya ayyuhal-ladhina amanu la tattakhidhu aduwwi",
          "tafsir":"Al-Mumtahana — Imtihon etilgan. 13 oyat. Shayx Muhammad Sodiq: «Kofirlar bilan do'stlik chegarasi, mo'mina ayollarni qabul qilish va ularni sinash qoidalari bayon etilgan.»"},
    61:  {"name":"As-Sof",       "arabic":"الصف",        "ayat":14,
          "ar":"سَبَّحَ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
          "lat":"Sabbaha lillahi ma fis-samawati wa ma fil-ard",
          "tafsir":"As-Sof — Saflangan. 14 oyat. Shayx Muhammad Sodiq: «Iso alayhissalom Muhammad s.a.v. ni bashorat qilgani tasdiqlangan. Alloh yo'lida saflangan kurash — eng sevimli amal.»"},
    62:  {"name":"Al-Jumu'a",    "arabic":"الجمعة",      "ayat":11,
          "ar":"يُسَبِّحُ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
          "lat":"Yusabbihu lillahi ma fis-samawati wa ma fil-ard",
          "tafsir":"Al-Jumu'a — Juma. 11 oyat. Shayx Muhammad Sodiq: «Juma namozi farzi va unda tijoratni tark etish buyurilgan. Payg'ambar Juma kechasi shu surani o'qirdilar.»"},
    63:  {"name":"Al-Munofiqun", "arabic":"المنافقون",   "ayat":11,
          "ar":"إِذَا جَاءَكَ الْمُنَافِقُونَ",
          "lat":"Idha ja'akal-munafiqun",
          "tafsir":"Al-Munofiqun — Munofiqlar. 11 oyat. Shayx Muhammad Sodiq: «Munofiqning 3 belgisi: yolg'on gapiradi, va'dasini buzdiradi, amonatga xiyonat qiladi. Bu surada ularni tanish belgilari bayon etilgan.»"},
    64:  {"name":"At-Tagobun",   "arabic":"التغابن",     "ayat":18,
          "ar":"يُسَبِّحُ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
          "lat":"Yusabbihu lillahi ma fis-samawati wa ma fil-ard",
          "tafsir":"At-Tagobun — Aldanish. 64 oyat. Shayx Muhammad Sodiq: «Qiyomat kuni yutqazganlar va yutqazmaganlar aniqlanadi. Farzand va xotin — fitnadan ehtiyot bo'ling, ammo ular bilan yaxshi muomala qiling.»"},
    65:  {"name":"At-Taloq",     "arabic":"الطلاق",      "ayat":12,
          "ar":"يَا أَيُّهَا النَّبِيُّ إِذَا طَلَّقْتُمُ النِّسَاءَ",
          "lat":"Ya ayyuhan-nabiyyu idha tallaqtumun-nisa'",
          "tafsir":"At-Taloq — Talaq. 12 oyat. Shayx Muhammad Sodiq: «Talaq qoidalari, idda muddati va xotin haqqini to'lash Islomda qat'iy belgilangan. Alloh har qiyinchilikdan chiqish yo'lini ochadi.»"},
    66:  {"name":"At-Tahrim",    "arabic":"التحريم",     "ayat":12,
          "ar":"يَا أَيُّهَا النَّبِيُّ لِمَ تُحَرِّمُ",
          "lat":"Ya ayyuhan-nabiyyu lima tuharrimu",
          "tafsir":"At-Tahrim — Taqiqlash. 12 oyat. Shayx Muhammad Sodiq: «Payg'ambar o'zi uchun halolni harom qilgani va Alloh uni tuzatgani. Oila ichidagi munosabatlar va Alloh oldida javobgarlik.»"},
    67:  {"name":"Al-Mulk",      "arabic":"الملك",       "ayat":30,
          "ar":"تَبَارَكَ الَّذِي بِيَدِهِ الْمُلْكُ",
          "lat":"Tabarakal-ladhi biyadihil-mulk",
          "tafsir":"Al-Mulk — Saltanat. 30 oyat. Shayx Muhammad Sodiq: «Bu surani har kecha uxlashdan oldin o'qing — qabr azobidan himoya. Payg'ambar (s.a.v.) uni hech qachon tark etmaganlar.»"},
    68:  {"name":"Al-Qalam",     "arabic":"القلم",       "ayat":52,
          "ar":"نٓ وَالْقَلَمِ وَمَا يَسْطُرُونَ",
          "lat":"Nun, wal-qalami wa ma yasthurun",
          "tafsir":"Al-Qalam — Qalam. 52 oyat. Shayx Muhammad Sodiq: «Birinchi oyatda qalam ulug'langan — ilm va yozuv muqaddasdir. Payg'ambarning oliy axloqi ulug'langan.»"},
    69:  {"name":"Al-Hoqqa",     "arabic":"الحاقة",      "ayat":52,
          "ar":"الْحَاقَّةُ",
          "lat":"Al-Haqqah",
          "tafsir":"Al-Hoqqa — Haqiqat. 52 oyat. Shayx Muhammad Sodiq: «Qiyomat — bu mutlaq haqiqat. Ad va Samud qabilalarining halokati, Nuh tufoni — barchasi Allohning qudratini ko'rsatadi.»"},
    70:  {"name":"Al-Ma'orij",   "arabic":"المعارج",     "ayat":44,
          "ar":"سَأَلَ سَائِلٌ بِعَذَابٍ وَاقِعٍ",
          "lat":"Sa'ala sa'ilun bi-adhabi waqi'",
          "tafsir":"Al-Ma'orij — Ko'tarilish joylari. 44 oyat. Shayx Muhammad Sodiq: «Alloh oldida bir kun — 50 ming yilga teng. Mo'min insoning fazilatlari va namozni asrab qolish ahamiyati bayon etilgan.»"},
    71:  {"name":"Nuh",          "arabic":"نوح",         "ayat":28,
          "ar":"إِنَّا أَرْسَلْنَا نُوحًا إِلَىٰ قَوْمِهِ",
          "lat":"Inna arsalna Nuhan ila qawmihi",
          "tafsir":"Nuh — Nuh alayhissalom. 28 oyat. Shayx Muhammad Sodiq: «Nuh alayhissalom 950 yil da'vat qildi. Uning sabri va charchashini bilmas qat'iyatidan ibrat olaylik.»"},
    72:  {"name":"Al-Jinn",      "arabic":"الجن",        "ayat":28,
          "ar":"قُلْ أُوحِيَ إِلَيَّ أَنَّهُ اسْتَمَعَ نَفَرٌ مِّنَ الْجِنِّ",
          "lat":"Qul uhiya ilayya annahu istama'a nafarun minal-jinn",
          "tafsir":"Al-Jinn — Jinlar. 28 oyat. Shayx Muhammad Sodiq: «Jinlar Qur'onni eshitib iymon keltirdi. Ular ham Allohga ibodat qilishga majbur. G'aybni faqat Alloh biladi.»"},
    73:  {"name":"Al-Muzzammil", "arabic":"المزمل",      "ayat":20,
          "ar":"يَا أَيُّهَا الْمُزَّمِّلُ",
          "lat":"Ya ayyuhal-muzzammil",
          "tafsir":"Al-Muzzammil — O'ranib olgan. 20 oyat. Shayx Muhammad Sodiq: «Tahajjud namozi buyurilgan. Qur'onni tartil bilan o'qish — shoshilmasdan, to'g'ri talaffuz bilan o'qish farmonlashtirilgan.»"},
    74:  {"name":"Al-Muddassir", "arabic":"المدثر",      "ayat":56,
          "ar":"يَا أَيُّهَا الْمُدَّثِّرُ",
          "lat":"Ya ayyuhal-muddassir",
          "tafsir":"Al-Muddassir — To'rga o'ranib olgan. 56 oyat. Shayx Muhammad Sodiq: «Da'vatni boshlash buyrugi. Do'zaxning 19 malayi. Allohning hidoyati va yo'ldosh qoldirishining hikmatli tasviri.»"},
    75:  {"name":"Al-Qiyoma",    "arabic":"القيامة",     "ayat":40,
          "ar":"لَا أُقْسِمُ بِيَوْمِ الْقِيَامَةِ",
          "lat":"La uqsimu bi-yawmil-qiyamah",
          "tafsir":"Al-Qiyoma — Qiyomat. 40 oyat. Shayx Muhammad Sodiq: «Inson o'z nafsiga guvohdir — ichida nima bor, yaxshi biladi. Qiyomat kuni yuzlar yorqin yoki qorong'i bo'lishi tasvirlangan.»"},
    76:  {"name":"Al-Inson",     "arabic":"الإنسان",     "ayat":31,
          "ar":"هَلْ أَتَىٰ عَلَى الْإِنسَانِ حِينٌ مِّنَ الدَّهْرِ",
          "lat":"Hal ata alal-insani hinun minad-dahr",
          "tafsir":"Al-Inson — Inson. 31 oyat. Shayx Muhammad Sodiq: «Jannat ahlining mukammal tavsifi. Ular sovuq suvdan ichirishadi va taom berishadi. Ibodat va zikrning ahamiyati ta'kidlangan.»"},
    77:  {"name":"Al-Mursalot",  "arabic":"المرسلات",    "ayat":50,
          "ar":"وَالْمُرْسَلَاتِ عُرْفًا",
          "lat":"Wal-mursalati urfan",
          "tafsir":"Al-Mursalot — Yuborilganlar. 50 oyat. Shayx Muhammad Sodiq: «10 marta «O'sha kuni yolg'onchilarga voy bo'lsin!» oyati takrorlanadi — har safar yangi gunoh yodga olinadi.»"},
    78:  {"name":"An-Naba",      "arabic":"النبأ",       "ayat":40,
          "ar":"عَمَّ يَتَسَاءَلُونَ",
          "lat":"'Amma yatasa'alun",
          "tafsir":"An-Naba — Ulug' xabar. 40 oyat. Shayx Muhammad Sodiq: «Bu sura Qiyomat kuni va uning belgilari haqida. Kichik suralarga kiradi, ammo savob katta.»"},
    79:  {"name":"An-Nozi'ot",   "arabic":"النازعات",    "ayat":46,
          "ar":"وَالنَّازِعَاتِ غَرْقًا",
          "lat":"Wan-nazi'ati gharqa",
          "tafsir":"An-Nozi'ot — Qattiq tortuvchilar. 46 oyat. Shayx Muhammad Sodiq: «Farishtallar, Muso va Fir'avn qissasi va Qiyomat sahналари batafsil tasvirlangan.»"},
    80:  {"name":"Abasa",        "arabic":"عبس",         "ayat":42,
          "ar":"عَبَسَ وَتَوَلَّىٰ",
          "lat":"'Abasa wa tawalla",
          "tafsir":"Abasa — Qovushdi. 42 oyat. Shayx Muhammad Sodiq: «Ko'r sahobani e'tiborsiz qoldirganlik uchun Payg'ambarga ogohlantirildi. Alloh oldida hamma teng — boy-kambag'al farq yo'q.»"},
    81:  {"name":"At-Takwir",    "arabic":"التكوير",     "ayat":29,
          "ar":"إِذَا الشَّمْسُ كُوِّرَتْ",
          "lat":"Idhas-shamsu kuwwirat",
          "tafsir":"At-Takwir — O'rab qo'yish. 29 oyat. Shayx Muhammad Sodiq: «Qiyomat kuni quyosh o'rab qo'yiladi. Bu surani o'qiganda qiyomat ko'z oldiga keladi — yurakni yumshating.»"},
    82:  {"name":"Al-Infitor",   "arabic":"الانفطار",    "ayat":19,
          "ar":"إِذَا السَّمَاءُ انفَطَرَتْ",
          "lat":"Idhas-sama'un fatanat",
          "tafsir":"Al-Infitor — Yorilish. 19 oyat. Shayx Muhammad Sodiq: «Osmon yoriladi, yulduzlar to'kiladi, dengizlar qo'shiladi. Inson nima uchun Rabbiga nisbatan aldanadi?»"},
    83:  {"name":"Al-Mutaffifin","arabic":"المطففين",    "ayat":36,
          "ar":"وَيْلٌ لِّلْمُطَفِّفِينَ",
          "lat":"Waylun lil-mutaffifin",
          "tafsir":"Al-Mutaffifin — O'g'irlab tortuvchilar. 36 oyat. Shayx Muhammad Sodiq: «Tarozida aldash — katta gunoh. Savdo-sotiqda halollik — Islomning asosiy talabi. Ilyin va Sijjin — yaxshi va yomon amallar kitobi.»"},
    84:  {"name":"Al-Inshiqoq",  "arabic":"الانشقاق",    "ayat":25,
          "ar":"إِذَا السَّمَاءُ انشَقَّتْ",
          "lat":"Idhas-sama'un shaqqat",
          "tafsir":"Al-Inshiqoq — Yorilish. 25 oyat. Shayx Muhammad Sodiq: «Inson Allohga tomon mehnat qilib boradi va uni uchraydi. Kim kitobini o'ng qo'lidan olsa — oson hisob. Chap qo'ldan olsa — do'zax.»"},
    85:  {"name":"Al-Buruj",     "arabic":"البروج",      "ayat":22,
          "ar":"وَالسَّمَاءِ ذَاتِ الْبُرُوجِ",
          "lat":"Was-sama'i dhatil-buruj",
          "tafsir":"Al-Buruj — Burjlar. 22 oyat. Shayx Muhammad Sodiq: «Xandaq qazib mo'minlarni yoqqan zolimlar va ularning oqibati. Iymon uchun azob chekkanlar — eng ulug' sharofat.»"},
    86:  {"name":"At-Toriq",     "arabic":"الطارق",      "ayat":17,
          "ar":"وَالسَّمَاءِ وَالطَّارِقِ",
          "lat":"Was-sama'i wat-tariq",
          "tafsir":"At-Toriq — Kechqurun keluvchi. 17 oyat. Shayx Muhammad Sodiq: «Har jonzotning qo'riqchisi bor. Qur'on — ajratuvchi so'z. Kofirlar hiyla quradi, Alloh ham hiyla quradi — va Allohning hiylasi kuchliroq.»"},
    87:  {"name":"Al-A'lo",      "arabic":"الأعلى",      "ayat":19,
          "ar":"سَبِّحِ اسْمَ رَبِّكَ الْأَعْلَى",
          "lat":"Sabbihi smar rabbikal-a'la",
          "tafsir":"Al-A'lo — Eng yuqori. 19 oyat. Shayx Muhammad Sodiq: «Payg'ambar Vitr namozida shu surani o'qirdilar. Alloh yaratgan, yo'l ko'rsatgan va o'tloq chiqargan. Oxirat — dunyodan yaxshiroq.»"},
    88:  {"name":"Al-G'oshiya",  "arabic":"الغاشية",     "ayat":26,
          "ar":"هَلْ أَتَاكَ حَدِيثُ الْغَاشِيَةِ",
          "lat":"Hal ataka hadithul-ghashiyah",
          "tafsir":"Al-G'oshiya — Qoplovchi. 26 oyat. Shayx Muhammad Sodiq: «Qiyomat kuni yuzlar xor, yuzlar yorqin bo'ladi. Tuyalar, osmonu yer va tog'lar yaratilishidan ibrat oling. Payg'ambar bu surani o'qib eslatardi.»"},
    89:  {"name":"Al-Fajr",      "arabic":"الفجر",       "ayat":30,
          "ar":"وَالْفَجْرِ",
          "lat":"Wal-fajr",
          "tafsir":"Al-Fajr — Tong. 30 oyat. Shayx Muhammad Sodiq: «Ad, Samud va Fir'avn — uch zolim xalqning halokati. Qoniqgan nafs Allohga qaytadi — bu surada jannat ahlining yuqori holati tasvirlangan.»"},
    90:  {"name":"Al-Balad",     "arabic":"البلد",       "ayat":20,
          "ar":"لَا أُقْسِمُ بِهَٰذَا الْبَلَدِ",
          "lat":"La uqsimu bi-hadhal-balad",
          "tafsir":"Al-Balad — Shahar (Makka). 20 oyat. Shayx Muhammad Sodiq: «Inson tug'ilishdan qiyinchilikda. Ikki yo'l — yaxshilik va yomonlik. Qiyinchilikdan o'tish — to'yg'izish, yetim boqish.»"},
    91:  {"name":"Ash-Shams",    "arabic":"الشمس",       "ayat":15,
          "ar":"وَالشَّمْسِ وَضُحَاهَا",
          "lat":"Wash-shamsi wa duhaha",
          "tafsir":"Ash-Shams — Quyosh. 15 oyat. Shayx Muhammad Sodiq: «7 ta qasam — quyosh, oy, kun, kecha, osmon, yer, nafs. Nafsni poklagan baxtli, uni bulg'agan halokatga yuz tutgan.»"},
    92:  {"name":"Al-Layl",      "arabic":"الليل",       "ayat":21,
          "ar":"وَاللَّيْلِ إِذَا يَغْشَىٰ",
          "lat":"Wal-layli idha yaghsha",
          "tafsir":"Al-Layl — Kecha. 21 oyat. Shayx Muhammad Sodiq: «Ikki yo'l: berish va taqvolilik — oson yo'l. Xasislik va o'zini boy bilish — qiyin yo'l. Alloh faqat qoniqgan kishiga rozi.»"},
    93:  {"name":"Ad-Duho",      "arabic":"الضحى",       "ayat":11,
          "ar":"وَالضُّحَىٰ",
          "lat":"Wad-duha",
          "tafsir":"Ad-Duho — Choshgoh. 11 oyat. Shayx Muhammad Sodiq: «Payg'ambar qiynalganida nozil bo'ldi. Alloh seni tark etmadi, yo'q qilmadi. Yetimni haqorat qilma, qalandarni haydama, Rabbingning ne'matini ayt.»"},
    94:  {"name":"Al-Inshiroh",  "arabic":"الإنشراح",    "ayat":8,
          "ar":"أَلَمْ نَشْرَحْ لَكَ صَدْرَكَ",
          "lat":"Alam nashrah laka sadrak",
          "tafsir":"Al-Inshiroh — Kengaytirish. 8 oyat. Shayx Muhammad Sodiq: ««Har qiyinchilik bilan birga osonlik bor» — ikki marta takrorlangan. Bu — Allohning va'dasi. Qiyinchilikda shoshilma, osonlik kelar.»"},
    95:  {"name":"At-Tin",       "arabic":"التين",       "ayat":8,
          "ar":"وَالتِّينِ وَالزَّيْتُونِ",
          "lat":"Wat-tini waz-zaytun",
          "tafsir":"At-Tin — Anjir. 8 oyat. Shayx Muhammad Sodiq: «Inson eng mukammal qilib yaratilgan — aql, ruh, jismoniy go'zallik bilan. So'ng eng past darajaga tushiriladi — iymon va amal uni saqlab qoladi.»"},
    96:  {"name":"Al-Alaq",      "arabic":"العلق",       "ayat":19,
          "ar":"اقْرَأْ بِاسْمِ رَبِّكَ الَّذِي خَلَقَ",
          "lat":"Iqra' bismi rabbikal-ladhi khalaq",
          "tafsir":"Al-Alaq — Pıhtı. 19 oyat. Shayx Muhammad Sodiq: «Qur'onning birinchi nozil bo'lgan oyatlari. «O'qi!» — birinchi buyruq. Ilm — Islomda farz. Sajda oyati mavjud.»"},
    97:  {"name":"Al-Qadr",      "arabic":"القدر",       "ayat":5,
          "ar":"إِنَّا أَنزَلْنَاهُ فِي لَيْلَةِ الْقَدْرِ",
          "lat":"Inna anzalnahu fi laylatal-qadr",
          "tafsir":"Al-Qadr — Qadr. 5 oyat. Shayx Muhammad Sodiq: «Qadr kechasi ming oydan yaxshiroq — 83 yildan ko'proq. Bu kechada farishtallar yerga tushadi. Romazonning oxirgi 10 kuni izlang.»"},
    98:  {"name":"Al-Bayyina",   "arabic":"البينة",      "ayat":8,
          "ar":"لَمْ يَكُنِ الَّذِينَ كَفَرُوا",
          "lat":"Lam yakunil-ladhina kafaru",
          "tafsir":"Al-Bayyina — Aniq dalil. 8 oyat. Shayx Muhammad Sodiq: «Ahli kitob Muhammad s.a.v. kelishini bilishardi — lekin ko'plari rad etdi. Din — xolislik va namoz, zakot.»"},
    99:  {"name":"Az-Zilzol",    "arabic":"الزلزلة",     "ayat":8,
          "ar":"إِذَا زُلْزِلَتِ الْأَرْضُ زِلْزَالَهَا",
          "lat":"Idha zulzilatil-ardu zilzalaha",
          "tafsir":"Az-Zilzol — Zilzila. 8 oyat. Shayx Muhammad Sodiq: «Yer o'z xabarlarini aytadi. Zarra qadar yaxshilik va yomonlik ko'rinadi. Hech narsa yashirin emas.»"},
    100: {"name":"Al-Odiyot",    "arabic":"العاديات",    "ayat":11,
          "ar":"وَالْعَادِيَاتِ ضَبْحًا",
          "lat":"Wal-'adiyati dabha",
          "tafsir":"Al-Odiyot — Chopayotganlar. 11 oyat. Shayx Muhammad Sodiq: «Ot — eng sodiq hayvon. Insonning esa Rabbiga nisbatan nankorligi tasvirlangan. Qabr ochilganda yashirin sirlar ma'lum bo'ladi.»"},
    101: {"name":"Al-Qori'a",    "arabic":"القارعة",     "ayat":11,
          "ar":"الْقَارِعَةُ",
          "lat":"Al-Qari'ah",
          "tafsir":"Al-Qori'a — Qoqqich. 11 oyat. Shayx Muhammad Sodiq: «Qiyomat kuni odamlar uchgan kapalaklardek, tog'lar yung kabidir. Amali og'ir bo'lsa — qoniqarli hayot. Engilsa — Haviya do'zaxida.»"},
    102: {"name":"At-Takosur",   "arabic":"التكاثر",     "ayat":8,
          "ar":"أَلْهَاكُمُ التَّكَاثُرُ",
          "lat":"Alhakumut-takasur",
          "tafsir":"At-Takosur — Ko'payish bo'yicha musobaqa. 8 oyat. Shayx Muhammad Sodiq: «Mol-mulk, farzand, mansab to'plash — qabrgacha band qiladi. So'ng ne'matdan so'ralasiz. Bu qisqa sura katta dars.»"},
    103: {"name":"Al-Asr",       "arabic":"العصر",       "ayat":3,
          "ar":"وَالْعَصْرِ",
          "lat":"Wal-'asr",
          "tafsir":"Al-Asr — Asr. 3 oyat. Shayx Muhammad Sodiq: «Bu sura 3 oyat, ammo unga Imom Shofei butun Qur'on maqomini beripdi. Inson — ziyonda, faqat 4 sifatni tutganlar bundan mustasno.»"},
    104: {"name":"Al-Humaza",    "arabic":"الهمزة",      "ayat":9,
          "ar":"وَيْلٌ لِّكُلِّ هُمَزَةٍ لُّمَزَةٍ",
          "lat":"Waylun li-kulli humazatil-lumazah",
          "tafsir":"Al-Humaza — G'iybatchi. 9 oyat. Shayx Muhammad Sodiq: «Odamlarni orqadan malamat qilib, boyligini sanab hayotida abadiylikka ishongan — Hutama do'zaxida.»"},
    105: {"name":"Al-Fil",       "arabic":"الفيل",       "ayat":5,
          "ar":"أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ",
          "lat":"Alam tara kayfa fa'ala rabbuka bi-ashabul-fil",
          "tafsir":"Al-Fil — Fil. 5 oyat. Shayx Muhammad Sodiq: «Abrahaning Makkani buzish niyati abobil qushlari tomonidan barham topdi. Payg'ambar tug'ilgan yili bu voqea yuz berdi.»"},
    106: {"name":"Quraysh",      "arabic":"قريش",        "ayat":4,
          "ar":"لِإِيلَافِ قُرَيْشٍ",
          "lat":"Li-ilafi quraysh",
          "tafsir":"Quraysh — Quraysh qabilasi. 4 oyat. Shayx Muhammad Sodiq: «Quraysh qabilasiga berilgan ikki safar ne'mati — qish va yoz. Alloh ularni ovqatlantirdi va xavfdan saqladi. Unga ibodat qiling.»"},
    107: {"name":"Al-Mo'un",     "arabic":"الماعون",     "ayat":7,
          "ar":"أَرَأَيْتَ الَّذِي يُكَذِّبُ بِالدِّينِ",
          "lat":"Ara'aytal-ladhi yukadhdhibu bid-din",
          "tafsir":"Al-Mo'un — Mayda yon'qimchilik. 7 oyat. Shayx Muhammad Sodiq: «Din — faqat namoz va ro'za emas. Yetimni haydash, miskinni to'yg'izmaslik — dinni yolg'on deb hisoblash.»"},
    108: {"name":"Al-Kavsar",    "arabic":"الكوثر",      "ayat":3,
          "ar":"إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
          "lat":"Inna a'taynaka-l-kawsar",
          "tafsir":"Al-Kavsar — Ko'payish. 3 oyat — Qur'onning eng qisqa surasi. Shayx Muhammad Sodiq: «Kavsar — jannatdagi havuz va Payg'ambarga berilgan barcha ne'mat. Bu sura dushmanlarni xo'rlashni bashorat qilgan.»"},
    109: {"name":"Al-Kofirun",   "arabic":"الكافرون",    "ayat":6,
          "ar":"قُلْ يَا أَيُّهَا الْكَافِرُونَ",
          "lat":"Qul ya ayyuhal-kafirun",
          "tafsir":"Al-Kofirun — Kofirlar. 6 oyat. Shayx Muhammad Sodiq: «Din — murosa qilish mumkin bo'lmagan soha. «Sizning diningiz sizga, mening dinim menga» — bu diniy bag'rikenglik, lekin iymonni sotish emas.»"},
    110: {"name":"An-Nasr",      "arabic":"النصر",       "ayat":3,
          "ar":"إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ",
          "lat":"Idha ja'a nasrullahi wal-fath",
          "tafsir":"An-Nasr — Yordam. 3 oyat. Shayx Muhammad Sodiq: «Bu sura Makkaning fath etilishidan keyin nozil bo'lgan. Payg'ambar bu surani o'z vafotig'i yaqinlashuvining ishorasi deb tushundilar.»"},
    111: {"name":"Al-Masad",     "arabic":"المسد",       "ayat":5,
          "ar":"تَبَّتْ يَدَا أَبِي لَهَبٍ وَتَبَّ",
          "lat":"Tabbat yada Abi Lahabin wa tabb",
          "tafsir":"Al-Masad — Nar. 5 oyat. Shayx Muhammad Sodiq: «Abu Lahab va xotini Qur'onda nomlangan kam odamlardan. Ular islomga qarshi faol kurashganlar. Bu — bashorat oyati, isbotlangan.»"},
    112: {"name":"Al-Ixlos",     "arabic":"الإخلاص",     "ayat":4,
          "ar":"قُلْ هُوَ اللَّهُ أَحَدٌ",
          "lat":"Qul huwallahu ahad",
          "tafsir":"Al-Ixlos — Xolislik. 4 oyat. Shayx Muhammad Sodiq: «Bu sura Qur'onning uchdan biriga teng — chunki Allohning zotini to'liq bayon etadi. Har kuni 3 marta o'qish — Qur'onni bir marta o'qigandek.»"},
    113: {"name":"Al-Falaq",     "arabic":"الفلق",       "ayat":5,
          "ar":"قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
          "lat":"Qul a'udhu bi-rabbil-falaq",
          "tafsir":"Al-Falaq — Tong. 5 oyat. Shayx Muhammad Sodiq: «Bu sura — panoh surasi. Uxlashdan oldin o'qing. Mehr, sehr, hasad va kecha yovuzliklaridan himoya. Falaq + Nas birga o'qilsa — to'liq himoya.»"},
    114: {"name":"An-Nas",       "arabic":"الناس",       "ayat":6,
          "ar":"قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
          "lat":"Qul a'udhu bi-rabbin-nas",
          "tafsir":"An-Nas — Odamlar. 6 oyat — Qur'onning oxirgi surasi. Shayx Muhammad Sodiq: «Allohga uch sifat — Rabb, Malik, Ilohi — bilan murojaat etiladi. Har kecha uxlashdan oldin o'qing — shayton vasvasidan himoya.»"},
}

PAGES_PER_PAGE = 16  # 4x4
SERIF  = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def _font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def create_quran_card(sura_num: int, sura: dict) -> bytes:
    W   = 1100
    PAD = 70
    GOLD  = (255, 212, 60)
    WHITE = (255, 255, 255)
    LIGHT = (238, 246, 240)
    LINE  = (100, 170, 120)

    fh  = _font(SANS_B, 32)
    fla = _font(SANS_B, 34)
    flb = _font(SANS_B, 28)
    ftx = _font(SANS,   26)
    fft = _font(SANS_B, 28)

    # Arabcha autofit
    ar_text  = sura["ar"]
    ar_size  = 160
    probe    = Image.new("RGB", (W, 10))
    probe_d  = ImageDraw.Draw(probe)
    while ar_size > 40:
        far = _font(SERIF, ar_size)
        b   = probe_d.textbbox((0, 0), ar_text, font=far)
        if b[2] - b[0] <= W - PAD * 2:
            break
        ar_size -= 5

    b    = probe_d.textbbox((0, 0), ar_text, font=far); ar_h  = b[3] - b[1]
    b    = probe_d.textbbox((0, 0), sura["lat"], font=fla); lat_h = b[3] - b[1]
    wrapped = textwrap.wrap(sura["tafsir"], width=58)
    tafsir_h = 42 + len(wrapped) * 34

    H = 30 + 54 + 10 + ar_h + 14 + lat_h + 22 + tafsir_h + 24 + 70
    H = max(650, H)

    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        draw.line([(0, y), (W, y)], fill=(
            int(20 + ratio * 12),
            int(80 + ratio * 22),
            int(50 + ratio * 14)
        ))

    draw.ellipse([(-90,-90),(220,220)], fill=(30,100,65))
    draw.ellipse([(W-220,H-220),(W+90,H+90)], fill=(22,85,58))
    draw.ellipse([(W-250,-65),(W-45,145)], fill=(25,92,60))
    draw.ellipse([(18,H-190),(210,H+70)], fill=(16,68,46))

    def cx(text, font):
        try:
            b = draw.textbbox((0, 0), text, font=font)
            return max(PAD, (W - (b[2] - b[0])) // 2)
        except:
            return PAD

    y = 24
    draw.text((cx("Qur'oniy oyat", fh), y), "Qur'oniy oyat", font=fh, fill=GOLD)
    y += 54
    draw.line([(PAD, y), (W-PAD, y)], fill=GOLD, width=2)
    y += 12
    draw.text((cx(ar_text, far), y), ar_text, font=far, fill=WHITE)
    y += ar_h + 14
    draw.text((cx(sura["lat"], fla), y), sura["lat"], font=fla, fill=GOLD)
    y += lat_h + 20
    draw.line([(PAD, y), (W-PAD, y)], fill=LINE, width=2)
    y += 18
    draw.text((PAD, y), "Tafsir:", font=flb, fill=GOLD)
    y += 42
    for line in wrapped:
        draw.text((PAD, y), line, font=ftx, fill=LIGHT)
        y += 34
    y_bot = H - 62
    draw.line([(PAD, y_bot), (W-PAD, y_bot)], fill=LINE, width=2)
    footer = f"{sura['name']} surasi  |  1-oyat"
    draw.text((cx(footer, fft), y_bot + 12), footer, font=fft, fill=GOLD)
    draw.line([(PAD, H - 14), (W-PAD, H - 14)], fill=GOLD, width=2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.read()

def get_audio_url(n): return f"https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/{n:03d}.mp3"

def get_sura_list_keyboard(page=1):
    builder = InlineKeyboardBuilder()
    nums  = sorted(SURAS.keys())
    start = (page - 1) * PAGES_PER_PAGE
    for num in nums[start:start + PAGES_PER_PAGE]:
        s = SURAS[num]
        builder.button(text=f"{num}. {s['name']}", callback_data=f"surah_{num}")
    builder.adjust(4)  # 4x4
    total = (len(nums) + PAGES_PER_PAGE - 1) // PAGES_PER_PAGE
    nav = []
    if page > 1:   nav.append(("⬅️", f"surah_page_{page-1}"))
    if page < total: nav.append(("➡️", f"surah_page_{page+1}"))
    for t, c in nav: builder.button(text=t, callback_data=c)
    if nav: builder.adjust(4, len(nav))
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(4)
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
        "🎵 <b>Qur'on audiolari — Mishary Rashid al-Afasy</b>\n\n"
        "Barcha 114 sura | Sura tanlang 👇",
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
            caption=f"🎵 <b>{sura_num}. {sura['name']} — {sura['arabic']}</b>\n({sura['ayat']} oyat) | Mishary Rashid al-Afasy"
        )
    except Exception:
        await callback.message.answer(
            f"<b>{sura_num}. {sura['name']}</b>\n<pre>{sura['ar']}</pre>\n<i>{sura['lat']}</i>\n\n📖 {sura['tafsir']}"
        )
    try:
        audio = URLInputFile(get_audio_url(sura_num), filename=f"{sura['name']}.mp3")
        await callback.message.answer_audio(audio=audio,
            title=f"{sura_num}. {sura['name']} — {sura['arabic']}",
            performer="Mishary Rashid al-Afasy",
            reply_markup=get_after_keyboard())
    except Exception:
        await callback.message.answer(f"🔗 Audio: {get_audio_url(sura_num)}", reply_markup=get_after_keyboard())
