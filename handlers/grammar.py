from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

GRAMMAR_TOPICS = [
    {
        "id": 1,
        "title": "Ot (الاسم)",
        "emoji": "📝",
        "description": "Arabchada otlar, ularning turlari va xususiyatlari",
        "content": """
📝 <b>Ot (الاسم - Al-Ism)</b>

Arabchada ot shaxs, narsa, joy yoki tushunchani bildiradi.

<b>🔵 Otlarning jinsi:</b>
• <b>Muzakkar (مذكر)</b> - erkak jins
  Misol: كِتَاب (kitob), بَيت (uy)
  
• <b>Muannath (مؤنث)</b> - urg'ochi jins
  Belgi: oxirida ة yoki و yoki ا
  Misol: مَدرَسَة (maktab), بِنت (qiz)

<b>🔵 Otlarning soni:</b>
• <b>Mufrаd (مفرد)</b> - birlik: كِتَاب (kitob)
• <b>Muθanna (مثنى)</b> - juftlik: كِتَابَان (ikki kitob)
• <b>Jаm' (جمع)</b> - ko'plik: كُتُب (kitoblar)

<b>🔵 Ko'plik yasash:</b>
Oddiy ko'plik: ون/ين (erkak), ات (urg'ochi)
كَاتِب → كَاتِبُون (yozuvchilar)
مُعَلِّمَة → مُعَلِّمَات (o'qituvchi xonimlar)

<b>🔵 Tarkibiy ko'plik (Jаm' taksir):</b>
كِتَاب → كُتُب
بَيت → بُيُوت
رَجُل → رِجَال
""",
        "quiz": {
            "question": "كِتَاب so'zining ko'pligi qaysi?",
            "options": ["كِتَابَات", "كُتُب", "كِتَابَان", "كَاتِبُون"],
            "answer": 1
        }
    },
    {
        "id": 2,
        "title": "Fe'l (الفعل)",
        "emoji": "⚡",
        "description": "Arabcha fe'llar, zamonlar va nisbatlar",
        "content": """
⚡ <b>Fe'l (الفعل - Al-Fi'l)</b>

Arabcha fe'l harakat yoki holatni bildiradi.

<b>🔵 Fe'l zamonlari:</b>
• <b>Mozi (ماضي)</b> - o'tgan zamon
  كَتَبَ = u yozdi
  
• <b>Muzori' (مضارع)</b> - hozir/kelasi zamon
  يَكتُبُ = u yozmoqda/yozadi

• <b>Amr (أمر)</b> - buyruq mayli
  اُكتُب = yoz!

<b>🔵 Fe'l nisbatlari:</b>
1. Shaxs: 1-shaxs, 2-shaxs, 3-shaxs
2. Jins: Muzakkar, Muannath
3. Son: Mufrаd, Muθanna, Jam'

<b>📌 Misol: كَتَبَ (yozdi)</b>
هُوَ كَتَبَ = u yozdi
هِيَ كَتَبَت = u (xonim) yozdi
أَنَا كَتَبتُ = men yozdim
نَحنُ كَتَبنَا = biz yozdik

<b>🔵 Asosiy fe'llar:</b>
ذَهَبَ - ketdi | جَاءَ - keldi
قَرَأَ - o'qidi | كَتَبَ - yozdi
قَالَ - dedi | سَمِعَ - eshitdi
""",
        "quiz": {
            "question": "يَكتُبُ fe'li qaysi zamonda?",
            "options": ["O'tgan zamon", "Hozir/kelasi zamon", "Buyruq mayli", "Shart mayli"],
            "answer": 1
        }
    },
    {
        "id": 3,
        "title": "Sifat (الصفة)",
        "emoji": "🎨",
        "description": "Arabcha sifatlar va ularning ot bilan muvofiqligi",
        "content": """
🎨 <b>Sifat (الصفة/النعت)</b>

Arabchada sifat doim otdan KEYIN keladi va otga muvofiq bo'ladi.

<b>🔵 Muvofiqlik qoidalari:</b>
1. <b>Jins:</b> Erkak ot → erkak sifat / Urg'ochi ot → urg'ochi sifat
2. <b>Son:</b> Birlik/Juftlik/Ko'plik mos bo'lishi kerak
3. <b>Ta'riflik:</b> Ot ال bilan kelsa, sifat ham ال bilan

<b>📌 Misollar:</b>
رَجُلٌ كَبِيرٌ = katta erkak (yoshi katta)
امرَأةٌ كَبِيرَةٌ = katta ayol
كِتَابٌ جَمِيلٌ = go'zal kitob
بَيتٌ كَبِيرٌ = katta uy
البَيتُ الكَبِيرُ = katta uy (ma'lum)

<b>🔵 Ko'p ishlatiladigan sifatlar:</b>
كَبِير - katta | صَغِير - kichik
جَمِيل - go'zal | قَبِيح - xunuk
جَدِيد - yangi | قَدِيم - eski
سَرِيع - tez | بَطِيء - sekin
صَعب - qiyin | سَهل - oson
""",
        "quiz": {
            "question": "Arabchada sifat otdan qayerda keladi?",
            "options": ["Otdan OLDIN", "Otdan KEYIN", "Jumlaning boshida", "Istalgan joyda"],
            "answer": 1
        }
    },
    {
        "id": 4,
        "title": "Olmosh (الضمير)",
        "emoji": "👤",
        "description": "Arabcha olmoshlar jadvali",
        "content": """
👤 <b>Olmosh (الضمير - Ad-Damir)</b>

Arabchada olmoshlar jinsga va songa qarab o'zgaradi.

<b>🔵 Shaxs olmoshlari:</b>

1-shaxs:
أَنَا (ana) = men
نَحنُ (nahnu) = biz

2-shaxs (erkak):
أَنتَ (anta) = sen
أَنتُم (antum) = sizlar

2-shaxs (urg'ochi):
أَنتِ (anti) = sen (xonim)
أَنتُنَّ (antunna) = sizlar (xonimlar)

3-shaxs (erkak):
هُوَ (huwa) = u
هُم (hum) = ular

3-shaxs (urg'ochi):
هِيَ (hiya) = u (xonim)
هُنَّ (hunna) = ular (xonimlar)

<b>🔵 Birikma olmoshlar (-ga birikadigan):</b>
ي- = mening | كَ- = sening | هُ- = uning
كِتَابِي = mening kitobim
كِتَابُكَ = sening kitobing
كِتَابُهُ = uning kitobi
""",
        "quiz": {
            "question": "أَنتِ olmoshi kimga ishlatiladi?",
            "options": ["Erkak kishiga", "Urg'ochi kishiga (sen)", "Ko'plikka", "3-shaxsga"],
            "answer": 1
        }
    },
    {
        "id": 5,
        "title": "Jumla tuzilishi",
        "emoji": "📐",
        "description": "Arab jumlasining asosiy tuzilishi",
        "content": """
📐 <b>Jumla tuzilishi</b>

Arabchada ikkita asosiy jumla turi mavjud:

<b>🔵 1. Ot jumlasi (الجملة الاسمية):</b>
Tuzilishi: Mubtado + Xabar
(Ega + Kesim - fe'lsiz)

المُبتَدَأ = ega (artikl bilan)
الخَبَر = xabar (nima qiladi/qanday)

📌 Misol:
البَيتُ كَبِيرٌ = Uy katta
(al-baytu - uy | kabīrun - katta)

الكِتَابُ جَدِيدٌ = Kitob yangi
مُحَمَّدٌ مُعَلِّمٌ = Muhammad o'qituvchi

<b>🔵 2. Fe'l jumlasi (الجملة الفعلية):</b>
Tuzilishi: Fe'l + Ega + To'ldiruvchi

📌 Misol:
ذَهَبَ الوَلَدُ = Bola ketdi
قَرَأَ الطَّالِبُ الكِتَابَ = Talaba kitobni o'qidi

<b>🔵 Muhim farq:</b>
O'zbekchada: Men kitobni o'qidim
Arabchada: O'qidim men kitobni
(Fe'l - Ega - To'ldiruvchi tartibida)
""",
        "quiz": {
            "question": "البَيتُ كَبِيرٌ jumlasida xabar qaysi so'z?",
            "options": ["البَيتُ", "كَبِيرٌ", "Ikkalasi ham", "Hech qaysi"],
            "answer": 1
        }
    },
]

@router.callback_query(F.data == "menu_grammar")
async def grammar_menu(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    for topic in GRAMMAR_TOPICS:
        builder.button(
            text=f"{topic['emoji']} {topic['title']}",
            callback_data=f"grammar_{topic['id']}"
        )
    
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "📚 <b>Arab grammatikasi</b>\n\n"
        "Arabcha grammatikani bosqichma-bosqich o'rganing.\n"
        "Mavzuni tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("grammar_"))
async def show_grammar_topic(callback: CallbackQuery):
    topic_id = int(callback.data.split("_")[1])
    topic = next((t for t in GRAMMAR_TOPICS if t['id'] == topic_id), None)
    
    if not topic:
        return
    
    builder = InlineKeyboardBuilder()
    
    if topic_id > 1:
        builder.button(text="⬅️", callback_data=f"grammar_{topic_id - 1}")
    
    builder.button(text=f"{topic_id}/{len(GRAMMAR_TOPICS)}", callback_data="menu_grammar")
    
    if topic_id < len(GRAMMAR_TOPICS):
        builder.button(text="➡️", callback_data=f"grammar_{topic_id + 1}")
    
    if topic_id > 1 and topic_id < len(GRAMMAR_TOPICS):
        builder.adjust(3)
    else:
        builder.adjust(2)
    
    builder.button(text="🧠 Bu mavzudan test", callback_data=f"test_grammar_{topic_id}")
    builder.button(text="⬅️ Grammatika menyusi", callback_data="menu_grammar")
    builder.adjust(*([3 if (topic_id > 1 and topic_id < len(GRAMMAR_TOPICS)) else 2]), 1, 1)
    
    await callback.message.edit_text(topic['content'], reply_markup=builder.as_markup())
    await callback.answer()
